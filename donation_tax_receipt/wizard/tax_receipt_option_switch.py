# -*- coding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for Odoo
#    Copyright (C) 2014-2017 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2017 Akretion France (www.akretion.com)
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class DonationTaxReceiptOptionSwitch(models.TransientModel):
    _name = 'donation.tax.receipt.option.switch'
    _description = 'Switch Donation Tax Receipt Option'

    donation_id = fields.Many2one(
        'donation.donation', string='Donation',
        default=lambda self: self._context.get('active_id'))
    new_tax_receipt_option = fields.Selection([
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Tax Receipt Option', required=True)

    @api.multi
    def switch(self):
        self.ensure_one()
        assert self.donation_id, 'Missing donation'
        assert not self.donation_id.tax_receipt_id,\
            'Already linked to a tax receipt'
        self.donation_id.tax_receipt_option = self.new_tax_receipt_option
        self.donation_id.generate_each_tax_receipt()
        return True
