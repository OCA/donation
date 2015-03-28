# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
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


class DonationCampaign(models.Model):
    _name = 'donation.campaign'
    _description = 'Code attributed for a Donation Campaign'
    _order = 'code'
    _rec_name = 'display_name'

    @api.one
    @api.depends('code', 'name')
    def _compute_display_name(self):
        name = self.name
        if self.code:
            name = u'[%s] %s' % (self.code, name)
        self.display_name = name

    code = fields.Char(string='Code', size=10)
    name = fields.Char(string='Name', required=True)
    display_name = fields.Char(
        string='Display Name', compute='_compute_display_name',
        readonly=True, store=True)
    start_date = fields.Date(
        string='Start Date', default=fields.Date.context_today)
    nota = fields.Text(string='Notes')
