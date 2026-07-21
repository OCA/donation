# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tax_receipt_option = fields.Selection(
        [
            ("none", "None"),
            ("each", "For Each Donation"),
            ("annual", "Annual Tax Receipt"),
        ],
        default="each",
        tracking=True,
    )
    tax_receipt_ids = fields.One2many(
        "donation.tax.receipt", "partner_id", string="Tax Receipts"
    )
    tax_receipt_count = fields.Integer(
        compute="_compute_tax_receipt_count",
        string="# of Tax Receipts",
    )
    donor_rank = fields.Integer(default=0)

    # I don't want to sync tax_receipt_option between parent and child
    # The field tax_receipt_option should be configured on the parent
    # and read on the parent

    @api.depends("tax_receipt_ids")
    def _compute_tax_receipt_count(self):
        for partner in self:
            partner.tax_receipt_count = len(partner.tax_receipt_ids.ids)

    @api.model_create_multi
    def create(self, vals_list):
        search_partner_mode = self.env.context.get("res_partner_search_mode")
        is_donor = search_partner_mode == "donor"
        if is_donor:
            for vals in vals_list:
                if "donor_rank" not in vals:
                    vals["donor_rank"] = 1
        return super().create(vals_list)

    def _prepare_donor_rank(self):
        self.ensure_one()
        return 0

    def _update_donor_rank(self):
        """This method is inherited in donation and donation_sale"""
        self.ensure_one()
        self.write({"donor_rank": self._prepare_donor_rank()})
