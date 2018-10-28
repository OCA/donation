# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('donation_ids.partner_id')
    def _compute_donation_count(self):
        res = self.env['donation.donation'].read_group(
            [('partner_id', 'in', self.ids)],
            ['partner_id'], ['partner_id'])
        for re in res:
            partner = self.browse(re['partner_id'][0])
            partner.donation_count = re['partner_id_count']

    donation_ids = fields.One2many(
        'donation.donation', 'partner_id', string='Donations',
        readonly=True)
    donation_count = fields.Integer(
        compute='_compute_donation_count', string="# of Donations",
        readonly=True)
