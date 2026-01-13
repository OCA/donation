# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    donation_ids = fields.One2many(
        "donation.donation", "partner_id", string="Donations", readonly=True
    )
    donation_count = fields.Integer(
        compute="_compute_donation_count", string="# of Donations", compute_sudo=True
    )

    @api.depends("donation_ids.partner_id")
    def _compute_donation_count(self):
        rg_res = self.env["donation.donation"]._read_group(
            [("partner_id", "in", self.ids), ("state", "=", "done")],
            groupby=["partner_id"],
            aggregates=["__count"],
        )
        mapped_data = {partner: count for (partner, count) in rg_res}
        for partner in self:
            partner.donation_count = mapped_data.get(partner.id, 0)

    def _prepare_donor_rank(self):
        rank = super()._prepare_donor_rank()
        rank += self.donation_count
        return rank
