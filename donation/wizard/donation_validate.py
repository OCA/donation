# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class DonationValidate(models.TransientModel):
    _name = 'donation.validate'
    _description = 'Validate Donations'

    @api.multi
    def run(self):
        self.ensure_one()
        assert self.env.context.get('active_model') == 'donation.donation',\
            'Source model must be donations'
        assert self.env.context.get('active_ids'), 'No donations selected'
        donations = self.env['donation.donation'].browse(
            self.env.context.get('active_ids'))
        donations.validate()
        return
