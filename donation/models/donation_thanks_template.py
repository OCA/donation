# Copyright 2019 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DonationThanksTemplate(models.Model):
    _name = "donation.thanks.template"
    _description = "Donation Thanks Letter Template"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        ondelete="cascade",
        default=lambda self: self.env.company,
    )
    text = fields.Text(translate=True)
    image = fields.Binary(attachment=True)
