# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for OpenERP
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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class donation_donation(orm.Model):
    _inherit = "donation.donation"

    def _tax_receipt_total(self, cr, uid, ids, name, arg, context=None):
        print "_tax_receipt_total ids=", ids
        res = {}
        for donation in self.browse(cr, uid, ids, context=context):
            total = 0.0
            # Do not consider other currencies for tax receipts
            # because, for the moment, only very very few countries
            # accept tax receipts from other countries, and never in another
            # currency. If you know such cases, please tell us and we will
            # update the code of this module
            if donation.currency_id == donation.company_id.currency_id:
                for line in donation.line_ids:
                    print "line product=", line.product_id.name
                    print "line.tax_receipt=", line.tax_receipt_ok
                    print "line product tax r=", line.product_id.tax_receipt_ok
                    # Filter the lines eligible for a tax receipt.
                    if line.tax_receipt_ok:
                        print "line AMOUNT=", line.amount
                        total += line.quantity * line.unit_price
            res[donation.id] = total
        print "_tax_receipt_total res=", total
        return res

    def _get_donations_from_lines(self, cr, uid, ids, context=None):
        return self.pool['donation.donation'].search(
            cr, uid, [('line_ids', 'in', ids)], context=context)

    _columns = {
        'tax_receipt_id': fields.many2one(
            'donation.tax.receipt', 'Tax Receipt', readonly=True,
            copy=False),
        'tax_receipt_option': fields.selection([
            ('none', 'None'),
            ('each', 'For Each Donation'),
            ('annual', 'Annual Tax Receipt'),
            ], 'Tax Receipt Option', states={'done': [('readonly', True)]}),
        'tax_receipt_total': fields.function(
            _tax_receipt_total, type='float', string='Tax Receipt Total',
            store={
                'donation.line': (
                    _get_donations_from_lines,
                    ['donation_id', 'quantity', 'unit_price', 'product_id'],
                    10),
                }),
        }

    def _prepare_tax_receipt(self, cr, uid, donation, context=None):
        vals = {
            'company_id': donation.company_id.id,
            'currency_id': donation.currency_id.id,
            'donation_date': donation.donation_date,
            'amount': donation.tax_receipt_total,
            'type': 'each',
            'partner_id': donation.partner_id.id,
            'number': self.pool['donation.tax.receipt'].get_tax_receipt_number(
                cr, uid, donation.donation_date, context=context),
        }
        print "_prepare_tax_receipt number=", vals
        return vals

    def validate(self, cr, uid, ids, context=None):
        res = super(donation_donation, self).validate(
            cr, uid, ids, context=None)
        donation = self.browse(cr, uid, ids[0], context=context)
        if (
                donation.tax_receipt_option == 'each'
                and donation.tax_receipt_total
                and not donation.tax_receipt_id):
            receipt_vals = self._prepare_tax_receipt(
                cr, uid, donation, context=context)
            receipt_id = self.pool['donation.tax.receipt'].create(
                cr, uid, receipt_vals, context=context)
            donation.write({'tax_receipt_id': receipt_id})
        return res

    def partner_id_change(
            self, cr, uid, ids, partner_id, company_id, context=None):
        res = super(donation_donation, self).partner_id_change(
            cr, uid, ids, partner_id, company_id, context=context)
        if 'value' not in res:
            res['value'] = {}
        if partner_id:
            partner = self.pool['res.partner'].browse(
                cr, uid, partner_id, context=context)
            res['value']['tax_receipt_option'] = partner.tax_receipt_option
        else:
            res['value']['tax_receipt_option'] = False
        return res

    def tax_receipt_option_change(
            self, cr, uid, ids, partner_id, tax_receipt_option, context=None):
        res = {}
        if partner_id:
            partner = self.pool['res.partner'].browse(
                cr, uid, partner_id, context=context)
            if (
                    partner.tax_receipt_option == 'annual'
                    and tax_receipt_option != 'annual'):
                res = {
                    'warning': {
                        'title': _('Error:'),
                        'message':
                        _('You cannot change the Tax Receipt '
                            'Option when it is Annual.'),
                        },
                    'value': {'tax_receipt_option': 'annual'},
                    }
        return res


class donation_line(orm.Model):
    _inherit = 'donation.line'

    _columns = {
        'tax_receipt_ok': fields.boolean(
            'Eligible for a Tax Receipt'),
        }

    def product_id_change(self, cr, uid, ids, product_id, context):
        res = super(donation_line, self).product_id_change(
            cr, uid, ids, product_id, context=context)
        if product_id:
            product = self.pool['product.product'].browse(
                cr, uid, product_id, context=context)
            res['value']['tax_receipt_ok'] = product.tax_receipt_ok
        else:
            res['value']['tax_receipt_ok'] = False
        return res


class donation_tax_receipt(orm.Model):
    _name = 'donation.tax.receipt'
    _description = "Tax Receipt for Donations"
    _order = 'id desc'
    _rec_name = 'number'

    _columns = {
        'number': fields.char('Receipt Number', size=32),
        'date': fields.date('Date', required=True),
        'donation_date': fields.date('Donation Date'),
        'amount': fields.float(
            'Amount', digits_compute=dp.get_precision('Account')),
        'currency_id': fields.many2one(
            'res.currency', 'Currency', required=True),
        'partner_id': fields.many2one(
            'res.partner', 'Donor', required=True),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
        'print_date': fields.date('Print Date'),
        'donation_ids': fields.one2many(
            'donation.donation', 'tax_receipt_id', 'Related Donations'),
        'type': fields.selection([
            ('each', 'For Each Donation'),
            ('annual', 'Annual Tax Receipt'),
            ], 'Type', required=True),
        }

    _defaults = {
        'company_id':
        lambda self, cr, uid, context:
        self.pool['res.company']._company_default_get(
            cr, uid, 'donation.tax.receipt', context=context),
        'date': fields.date.context_today,
        }

    def get_tax_receipt_number(self, cr, uid, date, context=None):
        # Search the approriate sequence
        assert date, 'Date is required'
        date_dt = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        seq_type = 'donation.tax.receipt.%s' % date_dt.year
        seq_type_ids = self.pool['ir.sequence.type'].search(
            cr, uid, [('code', '=', seq_type)], context=context)
        if len(seq_type_ids) != 1:
            raise orm.except_orm(
                _('Error:'),
                _("Missing Sequence Code '%s'. Please create it and "
                    "create the related Sequences for each company.")
                % seq_type)
        number = self.pool['ir.sequence'].next_by_code(
            cr, uid, seq_type, context=context)
        return number
