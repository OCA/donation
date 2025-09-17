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

    number = fields.Char(string="Receipt Number", tracking=True)
    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        index=True,
        tracking=True,
    )
    donation_date = fields.Date(tracking=True)
    amount = fields.Monetary(tracking=True)
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.company.currency_id.id,
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Donor",
        required=True,
        ondelete="restrict",
        domain=[("parent_id", "=", False)],
        index=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    print_date = fields.Date(tracking=True)
    type = fields.Selection(
        [("each", "One-Time Tax Receipt"), ("annual", "Annual Tax Receipt")],
        required=True,
        tracking=True,
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
        layout_xmlid = "donation_base.tax_receipt_email_template"
        ctx = dict(
            default_model=self._name,
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode="comment",
            default_email_layout_xmlid=layout_xmlid,
            force_email=True,
        )
        action = {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "target": "new",
            "context": ctx,
        }
        return action
