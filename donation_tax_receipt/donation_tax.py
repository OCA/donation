# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for Odoo
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero


class DonationDonation(models.Model):
    _inherit = "donation.donation"

    @api.one
    @api.depends(
        'line_ids', 'line_ids.quantity', 'line_ids.unit_price',
        'line_ids.tax_receipt_ok')
    def _tax_receipt_total(self):
        total = 0.0
        # Do not consider other currencies for tax receipts
        # because, for the moment, only very very few countries
        # accept tax receipts from other countries, and never in another
        # currency. If you know such cases, please tell us and we will
        # update the code of this module
        if self.currency_id == self.company_id.currency_id:
            for line in self.line_ids:
                # Filter the lines eligible for a tax receipt.
                if line.tax_receipt_ok:
                    total += line.quantity * line.unit_price
        self.tax_receipt_total = total

    tax_receipt_id = fields.Many2one(
        'donation.tax.receipt', string='Tax Receipt', readonly=True,
        copy=False, track_visibility='onchange')
    tax_receipt_option = fields.Selection([
        ('none', 'None'),
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Tax Receipt Option', states={'done': [('readonly', True)]},
        track_visibility='onchange')
    tax_receipt_total = fields.Float(
        compute='_tax_receipt_total', string='Eligible Tax Receipt Sub-total',
        store=True)

    @api.model
    def _prepare_tax_receipt(self):
        vals = {
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'donation_date': self.donation_date,
            'amount': self.tax_receipt_total,
            'type': 'each',
            'partner_id': self.partner_id.id,
        }
        return vals

    @api.one
    def generate_each_tax_receipt(self):
        prec = self.env['decimal.precision'].precision_get('Account')
        if (
                self.tax_receipt_option == 'each' and
                not self.tax_receipt_id and
                not float_is_zero(
                    self.tax_receipt_total, precision_digits=prec)):
            receipt_vals = self._prepare_tax_receipt()
            receipt = self.env['donation.tax.receipt'].create(receipt_vals)
            self.tax_receipt_id = receipt.id

    @api.one
    def validate(self):
        res = super(DonationDonation, self).validate()
        self.generate_each_tax_receipt()
        return res

    @api.one
    def done2cancel(self):
        if self.tax_receipt_id:
            raise Warning(
                _("You cannot cancel this donation because "
                    "it is linked to the tax receipt %s. You should first "
                    "delete this tax receipt (but it may not be legally "
                    "allowed).")
                % self.tax_receipt_id.number)
        return super(DonationDonation, self).done2cancel()

    @api.onchange('partner_id')
    def partner_id_change(self):
        super(DonationDonation, self).partner_id_change()
        self.tax_receipt_option =\
            self.partner_id and self.partner_id.tax_receipt_option or False

    @api.onchange('tax_receipt_option')
    def tax_receipt_option_change(self):
        res = {}
        if (
                self.partner_id and
                self.partner_id.tax_receipt_option == 'annual' and
                self.tax_receipt_option != 'annual'):
            res = {
                'warning': {
                    'title': _('Error:'),
                    'message':
                    _('You cannot change the Tax Receipt '
                        'Option when it is Annual.'),
                    },
                }
            self.tax_receipt_option = 'annual'
        return res


class DonationLine(models.Model):
    _inherit = 'donation.line'

    tax_receipt_ok = fields.Boolean(string='Eligible for a Tax Receipt')

    @api.onchange('product_id')
    def product_id_change(self):
        super(DonationLine, self).product_id_change()
        self.tax_receipt_ok =\
            self.product_id and self.product_id.tax_receipt_ok or False


class DonationTaxReceipt(models.Model):
    _name = 'donation.tax.receipt'
    _description = "Tax Receipt for Donations"
    _order = 'id desc'
    _rec_name = 'number'

    number = fields.Char(string='Receipt Number')
    date = fields.Date(
        string='Date', required=True, default=fields.Date.context_today)
    donation_date = fields.Date(string='Donation Date', required=True)
    amount = fields.Float(
        string='Amount', digits=dp.get_precision('Account'))
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True, ondelete='restrict')
    partner_id = fields.Many2one(
        'res.partner', string='Donor', required=True, ondelete='restrict')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'donation.tax.receipt'))
    print_date = fields.Date(string='Print Date')
    donation_ids = fields.One2many(
        'donation.donation', 'tax_receipt_id', string='Related Donations')
    type = fields.Selection([
        ('each', 'One-Time Tax Receipt'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Type', required=True)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals=None):
        if vals is None:
            vals = {}
        date = vals.get('donation_date')
        fiscalyear_id = self.env['account.fiscalyear'].find(
            dt=date, exception=True)
        # If date is False, it uses today, which is our default value
        # I use account_auto_fy_sequence here:
        vals['number'] = self.env['ir.sequence'].with_context(
            fiscalyear_id=fiscalyear_id).next_by_code('donation.tax.receipt')
        return super(DonationTaxReceipt, self).create(vals)
