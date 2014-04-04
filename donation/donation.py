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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class res_users(orm.Model):
    _inherit = 'res.users'

    _columns = {
        'context_donation_campaign_id': fields.many2one('donation.campaign', 'Donation Campaign User'), # begin with context_...
        }


class donation_donation(orm.Model):
    _name = 'donation.donation'
    _description = 'Donations'
    _order = 'id desc'
    _rec_name = 'number'

    def _compute_total(self, cr, uid, ids, name, arg, context=None):
        print "_compute_total ids=", ids
        res = {}  # key = ID, value : amount_total
        for donation in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in donation.line_ids:
                total += line.quantity * line.unit_price
            res[donation.id] = total
        print "_compute_total res=", total
        return res

    def _get_donation_from_lines(self, cr, uid, ids, context=None):
        res = self.pool['donation.donation'].search(
            cr, uid, [('line_ids', 'in', ids)], context=context)
        return res

    def _get_donation_currency(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for donation in self.browse(cr, uid, ids, context=context):
            if donation.journal_id.currency:
                res[donation.id] = donation.journal_id.currency.id
            else:
                res[donation.id] = donation.company_id.currency_id.id
        return res

    _columns = {
        'number': fields.char(
            'Donation Number', size=32, readonly=True),
        'currency_id': fields.function(
            _get_donation_currency, type='many2one', relation='res.currency',
            string='Currency'),
        'partner_id': fields.many2one(
            'res.partner', 'Donator', required=True,
            states={'done': [('readonly', True)]}),
        'check_total': fields.float(
            'Check Amount', digits_compute=dp.get_precision('Account'),
            states={'done': [('readonly', True)]}),
        'amount_total': fields.function(
            _compute_total, type='float', string='Amount Total', store={
                'donation.line': (_get_donation_from_lines, ['unit_price', 'quantity', 'donation_id'], 10),
            }),
        'donation_date': fields.date(
            'Donation Date', required=True,
            states={'done': [('readonly', True)]}),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True,
            states={'done': [('readonly', True)]}),
        'line_ids': fields.one2many(
            'donation.line', 'donation_id', 'Donation Lines',
            states={'done': [('readonly', True)]}),
        'move_id': fields.many2one(
            'account.move', 'Account Move', readonly=True),
        'journal_id': fields.many2one(
            'account.journal', 'Payment Method', required=True,
            domain=[('type', '=', 'donation')],
            states={'done': [('readonly', True)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ], 'State', readonly=True),
        'company_currency_id': fields.related(
            'company_id', 'currency_id', type='many2one',
            relation="res.currency", string="Company Currency"),
        #'origin_id': fields.many2one('donation.origin', 'Origin of Donation'),
        'donation_campaign_id': fields.many2one(
            'donation.campaign', 'Donation Campaign'),
        'create_uid': fields.many2one('res.users', 'Created by'),
    }

    def _get_default_currency(self, cr, uid, context=None):
        company_id = self.pool['res.company']._company_default_get(
            cr, uid, 'donation.donation', context=context)
        company = self.pool['res.company'].browse(
            cr, uid, company_id, context=context)
        return company.currency_id.id

    def _get_default_journal(self, cr, uid, context=None):
        (model, res_id) = self.pool['ir.model.data'].get_object_reference(cr, uid, 'donation', 'donation_journal')
        assert model == 'account.journal', 'Wrong model'
        return res_id
    
    def get_default_campaign(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context) # here "ids" = uid where uid contains user access rules
        return user.context_donation_campaign_id.id
    
         
   
    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, context: \
            self.pool['res.company']._company_default_get(
                cr, uid, 'donation.donation', context=context),
        'currency_id': _get_default_currency,
        'journal_id': _get_default_journal,
        'donation_campaign_id': get_default_campaign,
        }

    def _check_donation_date(self, cr, uid, ids):
        today_dt = datetime.today()
        today_str = today_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        for donation in self.browse(cr, uid, ids):
            if donation.donation_date > today_str:
                return False
        return True

    _constraints = [(
        _check_donation_date,
        "Date must be today or in the past",
        ['donation_date']
        )]

    _sql_constraints = [(
        'number_company_unique',
        'unique(company_id, number)',
        'A donation with this number already exists for this company'
        )]

    def _prepare_donation_move(self, cr, uid, donation, context=None):
        if context is None:
            context = {}

        if not donation.journal_id.default_debit_account_id:
            raise orm.except_orm(
                _('Error:'),
                _("Missing Default Debit Account on journal '%s'.")
                % donation.journal_id.name)

        context['account_period_prefer_normal'] = True
        period_search = self.pool['account.period'].find(
            cr, uid, donation.donation_date, context=context)
        assert len(period_search) == 1, 'We should get one period'
        period_id = period_search[0]

        movelines = []
        # Note : we can have negative donations for donators that use direct
        # debit when their direct debit rejected by the bank
        for donation_line in donation.line_ids:
            account_id = donation_line.product_id.property_account_income.id
            if not account_id:
                account_id = donation_line.product_id.categ_id.property_account_income_categ.id
            if not account_id:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing income account on product '%s' or on it's related product category") % donation_line.product_id.name)
            if donation_line.amount > 0:
                credit = donation_line.amount
                debit = 0
            else:
                debit = donation_line.amount * -1
                credit = 0
            movelines.append((0, 0, {
                'name': donation_line.product_id.name,
                'credit': credit,
                'debit': debit,
                'account_id': account_id,
                }))

        # counter-part
        if donation.amount_total > 0:
            debit = donation.amount_total
            credit = 0
        else:
            credit = donation.amount_total * -1
            debit = 0
        movelines.append(
            (0, 0, {
                'debit': debit,
                'credit': credit,
                'name': _('Don de %s') % donation.partner_id.name,
                'account_id': donation.journal_id.default_debit_account_id.id,
            }))

        vals = {
            'journal_id': donation.journal_id.id,
            'date': donation.donation_date,
            'period_id': period_id,
            'ref': _('Don %s de %s') % (donation.number, donation.partner_id.name),
            'line_id': movelines,
            }
        print "_prepare_donation_move vals=", vals
        return vals

    def validate(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only one ID accepted'
        donation = self.browse(cr, uid, ids[0], context=context)

        if not donation.line_ids:
            raise orm.except_orm(
                _('Error:'),
                _('Cannot validate a donation without lines!'))

        print "donation.check_total=", donation.check_total
        print "donation.amount_total=", donation.amount_total
        if donation.check_total != donation.amount_total:
            raise orm.except_orm(
                _('Error:'),
                _("The amount of the donation (%s) is different from the sum of the donation lines (%s).")
                % (donation.check_total, donation.amount_total))

        # We only manage donations of the same currency for the moment
        if donation.currency_id.id != donation.company_id.currency_id.id:
            raise orm.except_orm(
                _('Error:'),
                _("The donation is in currency '%s' but the company '%s' has a currency '%s'. We don't handle that for the moment.") % (donation.currency_id.name, donation.company_id.name, donation.company_id.currency_id.name)
                )

        donation_write_vals = {'state': 'done'}
        if donation.amount_total:
            move_vals = self._prepare_donation_move(
                cr, uid, donation, context=context)
            move_id = self.pool['account.move'].create(
                cr, uid, move_vals, context=context)

            self.pool['account.move'].post(cr, uid, [move_id], context=context)
            donation_write_vals['move_id'] = move_id

        if not donation.number:
            donation_write_vals['number'] = self.pool['ir.sequence'].next_by_code(
                cr, uid, 'donation.donation', context=context)

        self.write(cr, uid, donation.id, donation_write_vals, context=context)
        return

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['state'] = 'draft'
        default['move_id'] = False
        default['number'] = False
        res = super(donation_donation, self).copy(
            cr, uid, id, default=default, context=context)
        return res

    def partner_id_change(self, cr, uid, ids, partner_id, context=None):
        return {}

    def back_to_draft(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'only one ID for back2draft'
        donation = self.browse(cr, uid, ids[0], context=context)
        if donation.move_id:
            self.pool['account.move'].button_cancel(
                cr, uid, [donation.move_id.id], context=context)
            self.pool['account.move'].unlink(
                cr, uid, donation.move_id.id, context=context)
        donation.write({'state': 'draft'}, context=context)
        # TODO : does it work if the account.move is reconciled ??? It should not.
        return


class donation_line(orm.Model):
    _name = 'donation.line'
    _description = 'Donation Lines'
    _rec_name = 'product_id'

    def _compute_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.quantity * line.unit_price
        return res

    _columns = {
        'donation_id': fields.many2one(
            'donation.donation', 'Donation', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('donation_ok', '=', True)]),
        'quantity': fields.integer('Quantity'),
        'unit_price': fields.float(
            'Unit Price', digits_compute=dp.get_precision('Account')),
        'amount': fields.function(
            _compute_amount, string='Amount',
            digits_compute=dp.get_precision('Account'), store={
                'donation.line': (lambda self, cr, uid, ids, c={}: ids, ['quantity', 'unit_price'], 10),
                }),
        'sequence': fields.integer('Sequence'),
        }

    _defaults = {
        'quantity': 1,
        }

    def product_id_change(self, cr, uid, ids, product_id, context):
        res = {'value': {}}
        if product_id:
            product = self.pool['product.product'].browse(
                cr, uid, product_id, context=context)
            res['value']['unit_price'] = product.list_price
        return res


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'donation_ids': fields.one2many(
            'donation.donation', 'partner_id', 'Donations'),
        }


class account_journal(orm.Model):
    _inherit = 'account.journal'

    _columns = {
        'type': fields.selection([
            ('sale', 'Sale'),
            ('sale_refund', 'Sale Refund'),
            ('purchase', 'Purchase'),
            ('purchase_refund', 'Purchase Refund'),
            ('cash', 'Cash'),
            ('bank', 'Bank and Checks'),
            ('general', 'General'),
            ('situation', 'Opening/Closing Situation'),
            ('donation', 'Donation'),
            ], 'Type', size=32, required=True,
            help="Select 'Sale' for customer invoices journals. "
            "Select 'Purchase' for supplier invoices journals. "
            "Select 'Cash' or 'Bank' for journals that are used in "
            "customer or supplier payments. "
            "Select 'General' for miscellaneous operations journals. "
            "Select 'Opening/Closing Situation' for entries generated for "
            " new fiscal years. "
            "Select 'Donations' for donation journals."
            ),
        }


    
   
    
    
    
    
