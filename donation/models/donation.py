# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

logger = logging.getLogger(__name__)


class DonationDonation(models.Model):
    _name = "donation.donation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Donation"
    _order = "id desc"
    _check_company_auto = True

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        states={"done": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
        default=lambda self: self.env.company.currency_id,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Donor",
        required=True,
        index=True,
        states={"done": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
    )
    commercial_partner_id = fields.Many2one(
        related="partner_id.commercial_partner_id",
        string="Parent Donor",
        store=True,
        index=True,
    )
    # country_id is here to have stats per country
    country_id = fields.Many2one(
        "res.country",
        compute="_compute_country_id",
        store=True,
    )
    check_total = fields.Monetary(
        string="Check Amount",
        states={"done": [("readonly", True)]},
        currency_field="currency_id",
        tracking=True,
    )
    amount_total = fields.Monetary(
        compute="_compute_total",
        currency_field="currency_id",
        store=True,
        tracking=True,
    )
    amount_total_company_currency = fields.Monetary(
        compute="_compute_total",
        string="Amount Total in Company Currency",
        currency_field="company_currency_id",
        store=True,
    )
    donation_date = fields.Date(
        required=True,
        states={"done": [("readonly", True)]},
        index=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        states={"done": [("readonly", True)]},
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        "donation.line",
        "donation_id",
        string="Donation Lines",
        states={"done": [("readonly", True)]},
        copy=True,
    )
    move_id = fields.Many2one(
        "account.move",
        string="Account Move",
        readonly=True,
        copy=False,
        check_company=True,
    )
    number = fields.Char(
        required=True,
        copy=False,
        string="Donation Number",
        index=True,
        default=lambda self: _("New"),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        domain="[('company_id', '=', company_id), ('donation', '=', True)]",
        tracking=True,
        check_company=True,
        states={"done": [("readonly", True)]},
        default=lambda self: self.env.user.context_donation_payment_mode_id,
    )
    payment_ref = fields.Char(
        string="Payment Reference",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancel", "Cancelled")],
        readonly=True,
        copy=False,
        default="draft",
        index=True,
        tracking=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        store=True,
    )
    campaign_id = fields.Many2one(
        "donation.campaign",
        string="Donation Campaign",
        tracking=True,
        check_company=True,
        ondelete="restrict",
        default=lambda self: self.env.user.context_donation_campaign_id,
    )
    tax_receipt_id = fields.Many2one(
        "donation.tax.receipt",
        readonly=True,
        copy=False,
        tracking=True,
        check_company=True,
    )
    tax_receipt_option = fields.Selection(
        [
            ("none", "None"),
            ("each", "For Each Donation"),
            ("annual", "Annual Tax Receipt"),
        ],
        compute="_compute_tax_receipt_option",
        states={"done": [("readonly", True)]},
        index=True,
        tracking=True,
        precompute=True,
        store=True,
        readonly=False,
    )
    tax_receipt_total = fields.Monetary(
        compute="_compute_total",
        string="Tax Receipt Eligible Amount",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
        help="Eligible Tax Receipt Sub-total in Company Currency",
    )
    bank_statement_line_id = fields.Many2one(
        "account.bank.statement.line",
        string="Source Bank Statement Line",
        ondelete="restrict",
        readonly=True,
    )
    thanks_printed = fields.Boolean(
        copy=False,
        tracking=True,
        help="This field automatically becomes active when "
        "the thanks letter has been printed.",
    )
    thanks_template_id = fields.Many2one(
        "donation.thanks.template",
        ondelete="restrict",
        copy=False,
    )

    _sql_constraints = [
        (
            "bank_statement_line_uniq",
            "unique(bank_statement_line_id)",
            "A donation already exists for this bank statement line.",
        )
    ]

    @api.depends(
        "line_ids.unit_price",
        "line_ids.quantity",
        "line_ids.product_id",
        "donation_date",
        "currency_id",
        "company_id",
    )
    def _compute_total(self):
        for donation in self:
            total = tax_receipt_total = 0.0
            for line in donation.line_ids:
                line_total = line.quantity * line.unit_price
                total += line_total
                if line.tax_receipt_ok:
                    tax_receipt_total += line_total

            date = donation.donation_date or fields.Date.context_today(self)
            donation.amount_total = total
            donation_currency = donation.currency_id
            company_currency = donation.company_id.currency_id
            total_company_currency = donation_currency._convert(
                total, company_currency, donation.company_id, date
            )
            tax_receipt_total_cc = donation_currency._convert(
                tax_receipt_total,
                company_currency,
                donation.company_id,
                date,
            )
            donation.amount_total_company_currency = total_company_currency
            donation.tax_receipt_total = tax_receipt_total_cc

    # We don't want a depends on partner_id.country_id, because if the partner
    # moves to another country, we want to keep the old country for
    # past donations to have good statistics
    @api.depends("partner_id")
    def _compute_country_id(self):
        for donation in self:
            donation.country_id = donation.partner_id.country_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "company_id" in vals:
                self = self.with_company(vals["company_id"])
            if vals.get("number", _("New")) == _("New"):
                vals["number"] = self.env["ir.sequence"].next_by_code(
                    "donation.donation", sequence_date=vals.get("donation_date")
                ) or _("New")
        return super().create(vals_list)

    def _prepare_each_tax_receipt(self):
        self.ensure_one()
        vals = {
            "company_id": self.company_id.id,
            "currency_id": self.company_currency_id.id,
            "donation_date": self.donation_date,
            "amount": self.tax_receipt_total,
            "type": "each",
            "partner_id": self.commercial_partner_id.id,
        }
        return vals

    # TODO migration: remove 'journal' argument and use self.payment_mode_id.fixed_journal_id
    def _prepare_counterpart_move_line(
        self, total_company_cur, total_currency, journal
    ):
        self.ensure_one()
        journal = self.payment_mode_id.fixed_journal_id
        company = journal.company_id
        if self.company_currency_id.compare_amounts(total_company_cur, 0) > 0:
            debit = total_company_cur
            credit = 0
        else:
            credit = -total_company_cur
            debit = 0
        if self.bank_statement_line_id:
            account_id = company.donation_account_id.id
        else:
            if not company.account_journal_payment_debit_account_id:
                raise UserError(
                    _("Missing Outstanding Receipts Account on company '%s'.")
                    % company.display_name
                )
            payment_method = self.payment_mode_id.payment_method_id
            account_id = (
                journal.inbound_payment_method_line_ids.filtered(
                    lambda x: x.payment_method_id == payment_method
                ).payment_account_id.id
                or company.account_journal_payment_debit_account_id.id
            )
        vals = {
            "debit": debit,
            "credit": credit,
            "account_id": account_id,
            "partner_id": self.commercial_partner_id.id,
            "currency_id": self.currency_id.id,
            "amount_currency": total_currency,
            "name": self.number,
            "display_type": "payment_term",
        }
        return vals

    def _prepare_donation_move(self):
        self.ensure_one()
        if not self.bank_statement_line_id and not self.payment_mode_id.donation:
            raise UserError(
                _(
                    "The payment mode '%(pay_mode)s' selected on donation "
                    "%(donation)s is not a donation payment mode.",
                    pay_mode=self.payment_mode_id.display_name,
                    donation=self.display_name,
                )
            )
        assert self.payment_mode_id.bank_account_link == "fixed"
        journal = self.payment_mode_id.fixed_journal_id
        assert journal

        # Note : we can have negative donations for donors that use direct
        # debit when their direct debit rejected by the bank
        total_company_cur = 0.0
        total_currency = 0.0

        vals = {
            "company_id": self.company_id.id,
            "journal_id": journal.id,
            "date": self.donation_date,
            "ref": self.payment_ref,
            "line_ids": [],
        }

        for line in self.line_ids:
            if line.in_kind:
                continue
            if self.currency_id.is_zero(line.amount):
                continue
            account = line._get_account()
            if not account:
                raise UserError(
                    _("Failed to get account for donation line with product '%s'.")
                    % line.product_id.display_name
                )

            total_currency += line.amount

            amount_cc = self.currency_id._convert(
                line.amount,
                self.company_currency_id,
                self.company_id,
                self.donation_date,
            )
            total_company_cur += amount_cc
            if self.company_currency_id.compare_amounts(amount_cc, 0) > 0:
                credit = amount_cc
                debit = 0
            else:
                debit = -amount_cc
                credit = 0
            vals["line_ids"].append(
                (
                    0,
                    0,
                    {
                        "display_type": "product",
                        "product_id": line.product_id.id,
                        "credit": credit,
                        "debit": debit,
                        "account_id": account.id,
                        "analytic_distribution": line.analytic_distribution,
                        "partner_id": self.commercial_partner_id.id,
                        "currency_id": self.currency_id.id,
                        "amount_currency": -line.amount,
                    },
                )
            )

        if not vals["line_ids"]:
            return False

        # counter-part
        ml_vals = self._prepare_counterpart_move_line(
            total_company_cur, total_currency, journal
        )
        vals["line_ids"].append((0, 0, ml_vals))
        return vals

    def save_as_draft(self):
        # Used in simple form view used as wizard
        # Do nothing, just close
        self.ensure_one()
        return

    def validate(self):
        check_total_grp = self.env["res.users"].has_group(
            "donation.group_donation_check_total"
        )
        for donation in self:
            if donation.donation_date > fields.Date.context_today(self):
                raise UserError(
                    _(
                        "The date of donation %s should be today "
                        "or in the past, not in the future!"
                    )
                    % donation.display_name
                )
            if not donation.line_ids:
                raise UserError(
                    _(
                        "Cannot validate donation %s because it doesn't "
                        "have any lines!"
                    )
                    % donation.display_name
                )

            if donation.currency_id.is_zero(donation.amount_total):
                raise UserError(
                    _("Cannot validate donation %s because the total amount is 0!")
                    % donation.display_name
                )

            if donation.state != "draft":
                raise UserError(
                    _(
                        "Cannot validate donation %s because it is not "
                        "in draft state."
                    )
                    % donation.display_name
                )

            if (
                check_total_grp or donation.bank_statement_line_id
            ) and donation.currency_id.compare_amounts(
                donation.check_total, donation.amount_total
            ):
                raise UserError(
                    _(
                        "The amount of donation %(donation)s (%(check_total)s) is different "
                        "from the sum of the donation lines (%(amount_total)s).",
                        donation=donation.display_name,
                        check_total=format_amount(
                            self.env, donation.check_total, donation.currency_id
                        ),
                        amount_total=format_amount(
                            self.env, donation.amount_total, donation.currency_id
                        ),
                    )
                )
            full_in_kind = all([line.in_kind for line in donation.line_ids])
            if not donation.payment_mode_id and not full_in_kind:
                raise UserError(
                    _(
                        "Payment Mode is not set on donation %s (only fully "
                        "in-kind donations don't require a payment mode)."
                    )
                    % donation.display_name
                )

            vals = {"state": "done"}
            if full_in_kind and donation.payment_mode_id:
                vals["payment_mode_id"] = False

            if not full_in_kind:
                move_vals = donation._prepare_donation_move()
                # when we have a full in-kind donation: no account move
                if move_vals:
                    move = self.env["account.move"].create(move_vals)
                    move.with_context(validate_analytic=True)._post(soft=False)
                    vals["move_id"] = move.id
            else:
                donation.message_post(
                    body=_("Full in-kind donation: no account move generated")
                )

            receipt = donation.generate_each_tax_receipt()
            if receipt:
                vals["tax_receipt_id"] = receipt.id

            donation.write(vals)
            if donation.bank_statement_line_id:
                donation._reconcile_donation_from_bank_statement()
            donation.partner_id._update_donor_rank()
        return

    def _reconcile_donation_from_bank_statement(self):
        self.ensure_one()
        mlines_to_reconcile = self.env["account.move.line"]
        transit_account = self.company_id.donation_account_id
        if not transit_account:
            raise UserError(
                _(
                    "Donation %(donation)s is linked to a bank statement line, but "
                    "the Donation by Credit Transfer Account is not set for company "
                    "'%(company)s'. This should never happen.",
                    donation=self.display_name,
                    company=self.company_id.display_name,
                )
            )
        if not transit_account.reconcile:
            raise UserError(
                _(
                    "The Donation by Credit Transfer Account '%(account)s' "
                    "for company '%(company)s' is not reconciliable. "
                    "This should never happen.",
                    account=transit_account.display_name,
                    company=self.company_id.display_name,
                )
            )

        for donation_mline in self.move_id.line_ids:
            if (
                donation_mline.account_id == transit_account
                and not donation_mline.reconciled
            ):
                mlines_to_reconcile |= donation_mline
                logger.info(
                    "Found donation move line to reconcile ID=%d" % donation_mline.id
                )
                break
        for statement_mline in self.bank_statement_line_id.move_id.line_ids:
            if (
                statement_mline.account_id == transit_account
                and not statement_mline.reconciled
            ):
                mlines_to_reconcile |= statement_mline
                logger.info(
                    "Found bank statement move line to reconcile " "ID=%d",
                    statement_mline.id,
                )
                break
        if len(mlines_to_reconcile) == 2:
            mlines_to_reconcile.reconcile()
            logger.info(
                "Successfull reconcilation between donation and " "bank statement."
            )

    def generate_each_tax_receipt(self):
        self.ensure_one()
        receipt = False
        if (
            self.tax_receipt_option == "each"
            and not self.tax_receipt_id
            and not self.company_currency_id.is_zero(self.tax_receipt_total)
        ):
            receipt_vals = self._prepare_each_tax_receipt()
            receipt = self.env["donation.tax.receipt"].create(receipt_vals)
        return receipt

    def save_default_values(self):
        self.ensure_one()
        self.env.user.write(
            {
                "context_donation_payment_mode_id": self.payment_mode_id.id,
                "context_donation_campaign_id": self.campaign_id.id,
            }
        )

    def done2cancel(self):
        """from Done state to Cancel state"""
        for donation in self:
            if donation.tax_receipt_id:
                raise UserError(
                    _(
                        "You cannot cancel this donation because "
                        "it is linked to the tax receipt %s. You should first "
                        "delete this tax receipt (but it may not be legally "
                        "allowed)."
                    )
                    % donation.tax_receipt_id.display_name
                )
            if donation.move_id:
                donation.move_id.button_cancel()
                donation.with_context(force_delete=True).move_id.unlink()
            donation.write({"state": "cancel"})
            donation.partner_id._update_donor_rank()

    def cancel2draft(self):
        """from Cancel state to Draft state"""
        for donation in self:
            if donation.move_id:
                raise UserError(
                    _("A cancelled donation should not be linked to an account move")
                )
            if donation.tax_receipt_id:
                raise UserError(
                    _("A cancelled donation should not be linked to a tax receipt")
                )
        self.write({"state": "draft"})

    def unlink(self):
        for donation in self:
            if donation.state == "done":
                raise UserError(
                    _("The donation '%s' is in Done state, so you cannot delete it.")
                    % donation.display_name
                )
            if donation.move_id:
                raise UserError(
                    _(
                        "The donation '%s' is linked to an account move, "
                        "so you cannot delete it."
                    )
                    % donation.display_name
                )
            if donation.tax_receipt_id:
                raise UserError(
                    _(
                        "The donation '%(donation)s' is linked to the tax receipt "
                        "%(tax_receipt)s, so you cannot delete it.",
                        donation=donation.display_name,
                        tax_receipt=donation.tax_receipt_id.display_name,
                    )
                )
        return super().unlink()

    @api.depends("state", "number")
    def name_get(self):
        res = []
        for donation in self:
            name = donation.number
            if donation.state != "done":
                display_state = donation._fields["state"].convert_to_export(
                    donation.state, donation
                )
                name = "%s (%s)" % (name, display_state)
            res.append((donation.id, name))
        return res

    @api.depends("partner_id")
    def _compute_tax_receipt_option(self):
        for donation in self:
            donation.tax_receipt_option = (
                donation.partner_id
                and donation.partner_id.commercial_partner_id.tax_receipt_option
                or False
            )

    @api.onchange("tax_receipt_option")
    def tax_receipt_option_change(self):
        res = {}
        if (
            self.partner_id
            and self.partner_id.commercial_partner_id.tax_receipt_option == "annual"
            and self.tax_receipt_option != "annual"
        ):
            res = {
                "warning": {
                    "title": _("Error:"),
                    "message": _(
                        "You cannot change the Tax Receipt Option when it is Annual."
                    ),
                },
            }
            self.tax_receipt_option = "annual"
            return res

    def print_thanks(self):
        self.ensure_one()
        self.write({"thanks_printed": True})
        action = (
            self.env.ref("donation.report_thanks")
            .with_context(discard_logo_check=True)
            .report_action(self)
        )
        return action

    def thanks_printed_button(self):
        self.write({"thanks_printed": True})


class DonationLine(models.Model):
    _name = "donation.line"
    _description = "Donation Lines"
    _rec_name = "product_id"
    _inherit = "analytic.mixin"
    _check_company_auto = True

    donation_id = fields.Many2one("donation.donation", ondelete="cascade")
    currency_id = fields.Many2one(
        related="donation_id.currency_id",
        store=True,
    )
    company_id = fields.Many2one(related="donation_id.company_id", store=True)
    company_currency_id = fields.Many2one(
        related="donation_id.company_id.currency_id",
        string="Company Currency",
        store=True,
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("detailed_type", "like", "donation")],
        ondelete="restrict",
        check_company=True,
    )
    product_detailed_type = fields.Selection(
        related="product_id.detailed_type", store=True, string="Product Type"
    )
    quantity = fields.Integer(default=1)
    unit_price = fields.Monetary(currency_field="currency_id")
    amount = fields.Monetary(
        compute="_compute_amount",
        currency_field="currency_id",
        store=True,
    )
    amount_company_currency = fields.Monetary(
        compute="_compute_amount",
        string="Amount in Company Currency",
        currency_field="company_currency_id",
        store=True,
    )
    tax_receipt_amount = fields.Monetary(
        compute="_compute_amount",
        string="Tax Receipt Eligible Amount",
        currency_field="company_currency_id",
        store=True,
    )
    sequence = fields.Integer()
    # for the fields tax_receipt_ok and in_kind, we made an important change
    # between v8 and v9: in v8, it was a reglar field set by an onchange
    # in v9, it is a related stored field
    tax_receipt_ok = fields.Boolean(
        related="product_id.tax_receipt_ok",
        store=True,
    )
    in_kind = fields.Boolean(
        compute="_compute_in_kind",
        store=True,
    )

    @api.depends("product_id")
    def _compute_in_kind(self):
        for line in self:
            in_kind = False
            if (
                line.product_id.detailed_type
                and line.product_id.detailed_type.startswith("donation_in_kind")
            ):
                in_kind = True
            line.in_kind = in_kind

    @api.depends(
        "unit_price",
        "quantity",
        "product_id",
        "donation_id.currency_id",
        "donation_id.donation_date",
        "donation_id.company_id",
    )
    def _compute_amount(self):
        for line in self:
            amount = line.quantity * line.unit_price
            line.amount = amount
            donation_currency = line.donation_id.currency_id
            date = line.donation_id.donation_date or fields.Date.context_today(self)
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

    @api.depends("product_id")
    def _compute_analytic_distribution(self):
        for line in self:
            product = line.product_id
            if product:
                account = False
                try:
                    account = line._get_account()
                except Exception:
                    logger.warning(
                        "No income account configured for product %s",
                        product.display_name,
                    )
                distribution = self.env[
                    "account.analytic.distribution.model"
                ]._get_distribution(
                    {
                        "product_id": product.id,
                        "product_categ_id": product.categ_id.id,
                        "account_prefix": account and account.code or False,
                        "company_id": line.donation_id.company_id.id,
                    }
                )
                line.analytic_distribution = distribution or line.analytic_distribution

    @api.onchange("product_id")
    def product_id_change(self):
        for line in self:
            if line.product_id and line.product_id.list_price:
                # We should change that one day...
                line.unit_price = line.product_id.list_price

    def _get_account(self):
        # Method designed to be inherited (in donation_mass for example)
        self.ensure_one()
        account = self.with_company(
            self.company_id.id
        ).product_id._get_product_accounts()["income"]
        return account
