# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Thanks module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
