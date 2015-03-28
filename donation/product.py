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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    donation = fields.Boolean(
        string='Is a Donation',
        help="Specify if the product can be selected "
        "in a donation line.")
    in_kind_donation = fields.Boolean(
        string="In-Kind Donation")

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.sale_ok = False

    @api.onchange('in_kind_donation')
    def _in_kind_donation_change(self):
        if self.in_kind_donation:
            self.donation = True


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.sale_ok = False

    @api.onchange('in_kind_donation')
    def _in_kind_donation_change(self):
        if self.in_kind_donation:
            self.donation = True
