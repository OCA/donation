# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DonationTaxReceipt(models.Model):
    _name = "donation.tax.receipt"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Tax Receipt for Donations"
    _order = "id desc"
    _rec_name = "number"

    number = fields.Char(string="Receipt Number", default=lambda self: _("New"))
    date = fields.Date(
        string="Date", required=True, default=fields.Date.context_today, index=True
    )
    donation_date = fields.Date(string="Donation Date")
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.company.currency_id.id,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Donor",
        required=True,
        ondelete="restrict",
        domain=[("parent_id", "=", False)],
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    print_date = fields.Date(string="Print Date")
    type = fields.Selection(
        [("each", "One-Time Tax Receipt"), ("annual", "Annual Tax Receipt")],
        string="Type",
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "company_id" in vals:
                self = self.with_company(vals["company_id"])
            date = vals.get("donation_date")
            if vals.get("number", _("New")) == _("New"):
                vals["number"] = self.env["ir.sequence"].next_by_code(
                    "donation.tax.receipt", sequence_date=date
                ) or _("New")
        return super().create(vals_list)

    @api.model
    def update_tax_receipt_annual_dict(
        self, tax_receipt_annual_dict, start_date, end_date, company
    ):
        """This method is inherited in donation and donation_sale
        It is called by the tax.receipt.annual.create wizard"""

    def action_send_tax_receipt(self):
        self.ensure_one()
        if not self.partner_id.email:
            raise UserError(
                _("Missing email on partner '%s'.") % self.partner_id.display_name
            )
        template = self.env.ref("donation_base.tax_receipt_email_template")
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")
        ctx = dict(
            default_model="donation.tax.receipt",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode="comment",
        )
        action = {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }
        return action

    def action_print(self):
        self.ensure_one()
        return self.env.ref("donation_base.report_donation_tax_receipt").report_action(
            self
        )
