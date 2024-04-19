import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang



class DonationSummary(models.Model):
    _name = "donation.summary"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def _default_end_date(self):
        return datetime.date(fields.Date.context_today(self).year - 1, 12, 31)

    @api.model
    def _default_start_date(self):
        return datetime.date(fields.Date.context_today(self).year - 1, 1, 1)

    name = fields.Char(compute="_compute_name")

    is_summary_send = fields.Boolean(
        help="This field automatically becomes active when "
        "the summary has been send.",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Donor",
        index=True,
        states={"sent": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
        domain="[('donation_ids', '!=', False)]",
    )
    start_date = fields.Date(
        required=True,
        default=lambda self: self._default_start_date(),
        states={"sent": [("readonly", True)]},
    )
    end_date = fields.Date(
        required=True,
        default=lambda self: self._default_end_date(),
        states={"sent": [("readonly", True)]},
    )

    donation_ids = fields.One2many(
        "donation.donation",
        "donation_summary_id",
        string="Related Donations",
        compute="_compute_donation_ids",
        required=True,
        states={"sent": [("readonly", True)]},
    )

    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent")],
        readonly=True,
        copy=False,
        default="draft",
        index=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        ondelete="cascade",
        default=lambda self: self.env.company,
    )
    amount_total = fields.Monetary(
        tracking=True,
        compute="_compute_amounts",
        states={"sent": [("readonly", True)]},
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        states={"sent": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
        default=lambda self: self.env.company.currency_id,
    )
    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        domain=[("res_model", "=", "donation.summary")],
        string="Attachments",
    )

    def _compute_name(self):
        for rec in self:
            rec.name = (
                (rec.partner_id.name).replace(" ", "")
                + "_"
                + str(rec.start_date).replace("-", "")
                + "_"
                + str(rec.end_date).replace("-", "")
                if rec.partner_id
                else ""
            )

    def _prepare_donation_summary(self, existing_donation_ids):
        vals = {
            "partner_id": existing_donation_ids.partner_id.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "state": "draft",
            "is_summary_send": False,
        }
        return vals

    def massive_creation(self):
        d_sum = self.env["donation.summary"]
        donation_summary_ids = []
        for partner in self.donation_ids.partner_id.ids:
            donations = self.donation_ids.filtered(
                lambda donation: donation.partner_id.id == partner
            )
            values = self._prepare_donation_summary(donations)
            donation_summary_ids.append(values)
        if not len(donation_summary_ids):
            raise UserError(_("No annual tax receipt to generate"))

        self.unlink()

        for new_summary_vals in donation_summary_ids:
            d_sum.create(new_summary_vals)

        # Redireccionar a la vista tree
        return {
            "name": _("Donations Summary"),
            "type": "ir.actions.act_window",
            "res_model": "donation.summary",
            "view_type": "tree",
            "view_mode": "tree,form",
            "target": "main",
            "context": self.env.context,
        }

    @api.depends("donation_ids")
    def _compute_amounts(self):
        for rec in self:
            amount = 0
            for don in rec.donation_ids:
                amount += don.amount_total_company_currency
            rec.amount_total = amount

    @api.depends("partner_id", "start_date", "end_date")
    def _compute_donation_ids(self):
        for rec in self:
            domain = [("state", "=", "done"), ("donation_summary_id", "=", False)]
            if rec.partner_id:
                domain += [("partner_id", "=", rec.partner_id.id)]
            if rec.start_date and rec.end_date:
                domain += [
                    ("donation_date", ">=", rec.start_date),
                    ("donation_date", "<=", rec.end_date),
                ]
            donations = self.env["donation.donation"].search(domain)
            if not donations:
                raise UserError("There must be at least one donation in the summary.")
            rec.donation_ids = donations

    def massive_send_summary(self):
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        compose_form = self.env.ref(
            "donation_summary.donation_summary_send_wizard_form",
            raise_if_not_found=False,
        )
        ctx = dict(
            default_model="donation.summary",
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model="donation.summary",
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            mark_invoice_as_sent=True,
            default_email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
            force_email=True,
            active_ids=self.ids,
        )
        report_action = {
            "name": _("Send Donation Summary"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "donation.summary.send",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }
        return report_action

    def send_summary(self):
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref(
            "donation_summary.donation_summary_send_wizard_form",
            raise_if_not_found=False,
        )
        ctx = dict(
            default_model="donation.summary",
            default_res_id=self.id,
            default_res_model="donation.summary",
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            mark_invoice_as_sent=True,
            default_email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
            force_email=True,
            active_ids=self.ids,
        )
        report_action = {
            "name": _("Send Donation Summary"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "donation.summary.send",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

        return report_action

    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type
        """
        return "donation_summary.email_template_donation_summary"

    def action_print_donation_summary(self):
        """Print the certificate and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.filtered(lambda sum: not sum.is_summary_send).write(
            {"is_summary_send": True}
        )
        return self.env.ref("donation_summary.report_donation_summary").report_action(
            self
        )
