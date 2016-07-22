# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class DonationDonation(models.Model):
    _inherit = "donation.donation"

    thanks_printed = fields.Boolean(
        string='Thanks Printed',
        help="This field automatically becomes active when "
        "the thanks letter has been printed.")

    @api.multi
    def print_thanks(self):
        self.ensure_one()
        self.thanks_printed = True
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'donation.thanks',
            'datas': {'model': 'donation.donation', 'ids': self.ids},
            }
