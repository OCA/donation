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

    @api.depends("donation_ids.thanks_printed")
    def _compute_donation_send_thanks(self):
        for partner in self:
            if partner.donation_ids.filtered(lambda d: not d.thanks_printed):
                partner.donation_send_thanks = "yes"
            else:
                partner.donation_send_thanks = "no"

    donation_ids = fields.One2many(
        "donation.donation", "partner_id", string="Donations", readonly=True
    )
    donation_count = fields.Integer(
        compute="_compute_donation_count", string="# of Donations", compute_sudo=True
    )
    # Stored selection to search on the <field>
    donation_send_thanks = fields.Selection(
        string="Send Donation Thanks",
        selection=[("yes", "Yes"), ("no", "No")],
        compute="_compute_donation_send_thanks",
        store=True,
        help="""Filter on donors who (don't) need a thanks.\n
                Send it e.g. together with a newsletter.""",
    )

    def _prepare_donor_rank(self):
        rank = super()._prepare_donor_rank()
        rank += self.donation_count
        return rank
