# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DonationCampaign(models.Model):
    _name = "donation.campaign"
    _description = "Code attributed for a Donation Campaign"
    _order = "sequence, id"

    @api.depends("code", "name")
    def name_get(self):
        res = []
        for camp in self:
            name = camp.name
            if camp.code:
                name = "[{}] {}".format(camp.code, name)
            res.append((camp.id, name))
        return res

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    code = fields.Char("Code")
    name = fields.Char("Name", required=True)
    start_date = fields.Date("Start Date", default=fields.Date.context_today)
    # company_id is NOT required, it is empty by default
    company_id = fields.Many2one("res.company", string="Company", ondelete="cascade")
    note = fields.Text("Notes")

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique(code, company_id)",
            "A campaign with the same code already exists!",
        )
    ]

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        if name and operator == "ilike":
            recs = self.search([("code", "=", name)] + args, limit=limit)
            if recs:
                return recs.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
