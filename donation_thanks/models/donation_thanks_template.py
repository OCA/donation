# -*- coding: utf-8 -*-
# Copyright 2019 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class DonationThanksTemplate(models.Model):
    _name = "donation.thanks.template"
    _description = 'Donation Thanks Letter Template'

    name = fields.Char(required=True)
    active = fields.Boolean()
    company_id = fields.Many2one(
        'res.company', string='Company', ondelete='cascade',
        default=lambda self: self.env['res.company']._company_default_get())
    text = fields.Text(translate=True)
    image = fields.Binary()
