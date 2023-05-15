# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("donation_ids.partner_id")
    def _compute_donation_count(self):
        rg_res = self.env["donation.donation"].read_group(
            [("partner_id", "in", self.ids), ("state", "=", "done")],
            ["partner_id"],
            ["partner_id"],
        )
        mapped_data = {x["partner_id"][0]: x["partner_id_count"] for x in rg_res}
        for partner in self:
            partner.donation_count = mapped_data.get(partner.id, 0)

    donation_ids = fields.One2many(
        "donation.donation", "partner_id", string="Donations", readonly=True
    )
    donation_count = fields.Integer(
        compute="_compute_donation_count", string="# of Donations", compute_sudo=True
    )

    def _prepare_donor_rank(self):
        rank = super()._prepare_donor_rank()
        rank += self.donation_count
        return rank
