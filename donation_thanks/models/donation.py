# -*- coding: utf-8 -*-
# Copyright 2014-2019 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2019 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class DonationDonation(models.Model):
    _inherit = "donation.donation"

    thanks_printed = fields.Boolean(
        string='Thanks Printed',
        help="This field automatically becomes active when "
        "the thanks letter has been printed.")
    thanks_template_id = fields.Many2one(
        'donation.thanks.template', string='Thanks Template',
        ondelete='restrict', copy=False)

    def print_thanks(self):
        self.ensure_one()
        self.thanks_printed = True
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'donation.thanks',
            'datas': {'model': 'donation.donation', 'ids': self.ids},
            }
