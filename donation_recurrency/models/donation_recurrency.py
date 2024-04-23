from odoo import _, api, fields, models

# , Command
# from odoo.osv import expression
from odoo.exceptions import UserError

# , ValidationError
# from lxml import etree


class DonationRecurrency(models.Model):
    _name = "donation.recurrency"
    _description = "Donation Recurrency"
    # _order = "code, name asc"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "donation.recurrency.mixin",
        # "donation.donation",
    ]

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):

        arch, view = super(DonationRecurrency, self)._get_view(
            view_id, view_type, **options
        )
        if view_type == "form" and not self.env.user.has_group(
            "base.group_erp_manager"
        ):
            print("Is terminated ", self.is_terminated)
            print("Recurring next date ", self.recurring_next_date)
            for node in arch.xpath("//field[@name='recurring_next_date']"):
                node.set("readonly", "1")
        # if view_type == 'form' and self.is_terminated:
        #     print(self.recurring_next_date)
        #     for node in arch.xpath("//button[@name='recurring_create_donations']"):
        #         node.set('invisible', '1')

        return arch, view

    name = fields.Char()
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended")],
        # copy=False,
        # index=True,
        # tracking=True,
    )
    active = fields.Boolean(
        default=True,
    )
    number = fields.Char(
        required=True,
        copy=False,
        string="Recurrency - Donation Number",
        index=True,
        default=lambda self: _("New"),
        readonly=True,
        # states={"draft": [("readonly", False)]},
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Donor",
        required=True,
        index=True,
        # states={"done": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        "donation.recurrency.line",
        "donation_id",
        required=True,
        string="Donation Lines",
    )

    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        domain="[('company_id', '=', company_id), ('donation', '=', True)]",
        check_company=True,
        required=True,
        # default=partner_id.customer_payment_mode_id
        default=lambda self: self.env.user.context_donation_payment_mode_id,
    )
    campaign_id = fields.Many2one(
        "donation.campaign",
        string="Donation Campaign",
        # tracking=True,
        check_company=True,
        ondelete="restrict",
        default=lambda self: self.env.user.context_donation_campaign_id,
    )
    tax_receipt_option = fields.Selection(
        [
            ("none", "None"),
            ("each", "For Each Donation"),
            ("annual", "Annual Tax Receipt"),
        ],
        compute="_compute_tax_receipt_option",
        # index=True,
        # tracking=True,
        # precompute=True,
        # store=True,
        # readonly=False,
    )
    thanks_template_id = fields.Many2one(
        "donation.thanks.template",
        ondelete="restrict",
        # copy=False,
    )
    donation_date = fields.Date(
        # required=True,
        # states={"done": [("readonly", True)]},
        # index=True,
        # tracking=True,
    )
    note = fields.Text(string="Notes")
    is_terminated = fields.Boolean(string="Terminated", readonly=True, copy=False)
    terminate_reason_id = fields.Many2one(
        comodel_name="donation.terminate.reason",
        string="Termination Reason",
        ondelete="restrict",
        readonly=True,
        copy=False,
        tracking=True,
    )
    terminate_comment = fields.Text(
        string="Termination Comment",
        readonly=True,
        copy=False,
        tracking=True,
    )
    terminate_date = fields.Date(
        string="Termination Date",
        readonly=True,
        copy=False,
        tracking=True,
    )

    is_canceled = fields.Boolean(string="Canceled", default=False)
    last_date_donated = fields.Date()

    donation_count = fields.Integer(
        compute="_compute_donation_count", string="# of Donations"
    )

    _sql_constraints = [
        (
            "no_delete",
            "CHECK(active = TRUE)",
            "No se permite eliminar registros, solo archivarlos.",
        )
    ]

    def _prepare_value_for_stop(self, date_end):
        self.ensure_one()
        return {
            "date_end": date_end,
            "recurring_next_date": self.get_next_donation_date(
                self.next_period_date_start,
                self.recurring_donation_type,
                self.recurring_donation_offset,
                self.recurring_rule_type,
                self.recurring_interval,
                max_date_end=date_end,
            ),
        }

    @api.onchange("partner_id")
    def _payment_mode_id(self):
        self.payment_mode_id = self.partner_id.customer_payment_mode_id

    def stop(self, date_end, manual_renew_needed=False, post_message=True):
        """
        Put date_end on contract line
        We don't consider contract lines that end's before the new end date
        :param date_end: new date end for contract line
        :return: True
        """
        for rec in self:
            if date_end < rec.date_start:
                rec.cancel()
            else:
                if not rec.date_end or rec.date_end > date_end:
                    old_date_end = rec.date_end
                    rec.write(rec._prepare_value_for_stop(date_end))
                    if post_message:
                        msg = (
                            _(
                                """Recurrency stopped: <br/>
                            - <strong>End</strong>: %(old_end)s -- %(new_end)s
                            """
                            )
                            % {
                                "old_end": old_date_end,
                                "new_end": rec.date_end,
                            }
                        )
                        rec.message_post(body=msg)
                else:
                    rec.write(
                        {
                            "is_auto_renew": False,
                            "manual_renew_needed": manual_renew_needed,
                        }
                    )
        return True

    def _terminate_contract(
        self, terminate_reason_id, terminate_comment, terminate_date
    ):
        self.ensure_one()
        self.stop(terminate_date)
        self.write(
            {
                "is_terminated": True,
                "terminate_reason_id": terminate_reason_id.id,
                "terminate_comment": terminate_comment,
                "terminate_date": terminate_date,
            }
        )
        return True

    @api.depends("line_ids.donation_id")
    def _compute_donation_count(self):
        rg_res = self.env["donation.donation"].read_group(
            [("contract_id", "in", self.ids), ("state", "=", "done")],
            ["contract_id"],
            ["contract_id"],
        )
        mapped_data = {x["contract_id"][0]: x["contract_id_count"] for x in rg_res}
        for rec in self:
            rec.donation_count = mapped_data.get(rec.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "company_id" in vals:
                self = self.with_company(vals["company_id"])
            if vals.get("number", _("New")) == _("New"):
                vals["number"] = self.env["ir.sequence"].next_by_code(
                    "donation.recurrency", sequence_date=vals.get("date_start")
                ) or _("New")
            vals["name"] = vals["number"]
        return super().create(vals_list)

    def action_terminate_recurrency(self):
        self.ensure_one()
        context = {"default_contract_id": self.id}
        return {
            "type": "ir.actions.act_window",
            "name": _("Terminate Recurrency"),
            "res_model": "donation.recurrency.terminate",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    @api.depends("partner_id")
    def _compute_country_id(self):
        for donation in self:
            donation.country_id = donation.partner_id.country_id

    def _get_lines_to_donation(self, date_ref):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (contract.line recordset)
        """
        self.ensure_one()

        lines_donations = []
        if not self.line_ids:
            raise UserError(
                _("Cannot create recurrence %s because it doesn't " "have any lines!")
                % self.display_name
            )
        for line in self.line_ids:
            vals = {
                "product_id": line.product_id.id,
                "quantity": line.quantity,
                "unit_price": round(line.unit_price, 2),
                "currency_id": self.env.company.currency_id.id,
            }
            lines_donations.append(self.env["donation.line"].sudo().create(vals).id)
        return sorted(lines_donations)

    def _prepare_donation(self, date_donation):
        """Prepare the values for the generated donation record.

        :return: A vals dictionary
        """
        self.ensure_one()

        vals = {
            "partner_id": self.partner_id.id,
            "payment_mode_id": self.payment_mode_id.id,
            "company_id": self.company_id.id,
            "campaign_id": self.campaign_id.id,
            "tax_receipt_option": "annual",
            "thanks_template_id": self.thanks_template_id.id,
            "line_ids": [],
            "donation_date": date_donation,
            "contract_id": self.id,
        }

        return vals

    def _update_recurring_next_date(self):
        for rec in self:
            last_date_donated = rec.next_period_date_end
            rec.write(
                {
                    "last_date_donated": last_date_donated,
                }
            )

    def _prepare_recurring_donations_values(self, date_ref_don=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        donations_values = []
        for contract in self:
            if not date_ref_don:
                date_ref = contract.recurring_next_date
            else:
                date_ref = date_ref_don
            if not date_ref:
                continue
            donation_lines = contract._get_lines_to_donation(date_ref)
            if not donation_lines:
                continue
            donation_vals = contract._prepare_donation(date_ref)
            donation_vals["line_ids"] = [(6, 0, donation_lines)]
            donations_values.append(donation_vals)
            contract._update_recurring_next_date()
        return donations_values

    def recurring_create_donation(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        today = fields.Date.context_today(self)
        recurrency = self.filtered(lambda rec: rec.recurring_next_date <= today)
        donations = recurrency._recurring_create_donation()
        return donations

    def _get_related_donations(self):
        self.ensure_one()
        donations = self.env["donation.donation"].search(
            [
                (
                    "contract_id",
                    "in",
                    self.ids,
                )
            ]
        )
        return donations

    @api.model
    def _add_donation_origin(self, donations):
        for item in self:
            for don in donations & item._get_related_donations():
                don.message_post(
                    body=_(
                        "%(msg)s by recurrency."
                        "<a"
                        '    href="#" data-oe-model="%(model_name)s" '
                        '    data-oe-id="%(rec_id)s"'
                        ">%(rec_name)s"
                        "</a>"
                    )
                    % {
                        "msg": don._creation_message(),
                        "model_name": item._name,
                        "rec_id": item.id,
                        "rec_name": item.display_name,
                    }
                )

    def _recurring_create_donation(self, date_ref=False):
        donations_values = self._prepare_recurring_donations_values(date_ref)
        donations = self.env["donation.donation"].sudo().create(donations_values)
        self._add_donation_origin(donations)
        self._compute_recurring_next_date()
        return donations

    @api.model
    def _get_recurring_create_func(self, create_type="donation"):
        """
        Allows to retrieve the recurring create function depending
        on generate_type attribute
        """
        if create_type == "donation":
            return self.__class__._recurring_create_donation

    @api.model
    def _get_contracts_to_donation_domain(self, date_ref=None):
        """
        This method builds the domain to use to find all
        contracts (contract.contract) to invoice.
        :param date_ref: optional reference date to use instead of today
        :return: list (domain) usable on contract.contract
        """
        domain = []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain.extend([("recurring_next_date", "<=", date_ref)])
        return domain

    @api.model
    def _cron_recurring_create(self, date_ref=False, create_type="donation"):
        """
        The cron function in order to create recurrent documents
        from contracts.
        """
        _recurring_create_func = self._get_recurring_create_func(
            create_type=create_type
        )
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = self._get_contracts_to_donation_domain(date_ref)
        while self.search(domain):
            contracts = self.search(domain)
            companies = set(contracts.mapped("company_id"))
            for company in companies:
                contracts_to_donation = contracts.filtered(
                    lambda c: c.company_id == company
                    and (not c.date_end or c.recurring_next_date <= c.date_end)
                ).with_company(company)
                _recurring_create_func(contracts_to_donation, date_ref=False)
        return True

    @api.model
    def cron_recurring_create_donation(self, date_ref=None):
        return self._cron_recurring_create(date_ref, create_type="donation")

    def recurring_create_donations(self):
        for rec in self:
            continue_while = True
            while (
                rec.recurring_next_date
                and (not rec.date_end or rec.recurring_next_date <= rec.date_end)
                and continue_while
            ):
                continue_while = rec.recurring_create_donation()
                # if rec.date_end and rec.recurring_next_date:
                #     continue_while = rec.recurring_next_date <= rec.date_end
                # elif not rec.recurring_next_date:
                #     continue_while = False
                # else:
                #     continue_while = True
                # continue_while = rec.recurring_next_date and
                # (not rec.date_end or rec.recurring_next_date <= rec.date_end) and res


class DonationRecurrencyLine(models.Model):
    _name = "donation.recurrency.line"
    _description = "Donation  REC Lines"
    _rec_name = "product_id"
    _inherit = [
        "donation.line",
        "donation.recurrency.mixin",
    ]
    _description = "Donation Recurrency Lines"

    donation_id = fields.Many2one(
        "donation.recurrency",
        string="Donation Recurrency",
    )

    currency_id = fields.Many2one(
        related="donation_id.currency_id",
    )

    @api.depends(
        "unit_price",
        "quantity",
        "product_id",
        "donation_id.currency_id",
        "donation_id.company_id",
    )
    def _compute_amount(self):
        for line in self:
            amount = line.quantity * line.unit_price
            line.amount = amount
            donation_currency = line.donation_id.currency_id
            date = fields.Date.context_today(self)
            amount_company_currency = donation_currency._convert(
                amount,
                line.donation_id.company_id.currency_id,
                line.donation_id.company_id,
                date,
            )
            tax_receipt_amount_cc = 0.0
            if line.product_id.tax_receipt_ok:
                tax_receipt_amount_cc = amount_company_currency
            line.amount_company_currency = amount_company_currency
            line.tax_receipt_amount = tax_receipt_amount_cc
