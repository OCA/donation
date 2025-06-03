# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DonationCampaign(models.Model):
    _name = "donation.campaign"
    _description = "Code attributed for a Donation Campaign"
    _order = "sequence, id"
    _rec_names_search = ["name", "code"]

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    code = fields.Char()
    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.context_today)
    # company_id is NOT required, it is empty by default
    company_id = fields.Many2one("res.company", ondelete="cascade")
    note = fields.Text("Notes")

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique(code, company_id)",
            "A campaign with the same code already exists!",
        )
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for camp in self:
            name = camp.name
            if camp.code:
                name = f"[{camp.code}] {name}"
            camp.display_name = name
