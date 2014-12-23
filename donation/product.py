# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for OpenERP
#    Copyright (C) 2014 Barroux Abbey
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

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.sale_ok = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.sale_ok = False
