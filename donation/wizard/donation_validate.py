# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for Odoo
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

from openerp import models, api


class DonationValidate(models.TransientModel):
    _name = 'donation.validate'
    _description = 'Validate Donations'

    @api.one
    def run(self):
        assert self.env.context.get('active_model') == 'donation.donation',\
            'Source model must be donations'
        assert self.env.context.get('active_ids'), 'No donations selected'
        donations = self.env['donation.donation'].browse(
            self.env.context.get('active_ids'))
        donations.validate()
        return
