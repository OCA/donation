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
        'context_donation_campaign_id': fields.many2one(
            'donation.campaign', 'Current Donation Campaign'),
        # begin with context_ to allow user to change it by itself
        }


class donation_donation(orm.Model):
    _name = 'donation.donation'
    _description = 'Donations'
    _order = 'id desc'
    _rec_name = 'number'

    def _compute_total(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}  # key = ID, value : amount_total
        for donation in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in donation.line_ids:
                total += line.quantity * line.unit_price
            if donation.currency_id == donation.company_id.currency_id:
                total_company_currency = total
            else:
                ctx_convert = context.copy()
                ctx_convert['date'] = donation.donation_date
                total_company_currency = self.pool['res.currency'].compute(
                    cr, uid, donation.currency_id.id,
                    donation.company_id.currency_id.id, total,
                    context=ctx_convert)
            res[donation.id] = {
                'amount_total': total,
                'amount_total_company_currency': total_company_currency,
                }
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
            'res.partner', 'Donor', required=True,
            states={'done': [('readonly', True)]}),
        'check_total': fields.float(
            'Check Amount', digits_compute=dp.get_precision('Account'),
            states={'done': [('readonly', True)]}),
        'amount_total': fields.function(
            _compute_total, type='float', multi="donation",
            string='Amount Total', store={
                'donation.line': (_get_donation_from_lines, ['unit_price', 'quantity', 'donation_id'], 10),
            }),
        'amount_total_company_currency': fields.function(
            _compute_total, type='float', multi="donation",
            string='Amount Total in Company Currency', store={
                'donation.donation': (lambda self, cr, uid, ids, c={}: ids, ['currency_id', 'journal_id'], 10),
                'donation.line': (_get_donation_from_lines, ['unit_price', 'quantity', 'donation_id'], 20),
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


    def _get_analytic_account_id(
            self, cr, uid, donation_line, account_id, context=None):
        analytic_account_id = donation_line.analytic_account_id.id or False
        return analytic_account_id

    def _prepare_donation_move(self, cr, uid, donation, number, context=None):
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
        if donation.company_id.currency_id.id != donation.currency_id.id:
            currency_id = donation.currency_id.id
        else:
            currency_id = False
            total_amount_currency = 0.0
        # Note : we can have negative donations for donors that use direct
        # debit when their direct debit rejected by the bank
        amount_total_company_cur = 0.0
        name = _('Don de %s') % donation.partner_id.name

        aml = {}
        # key = (account_id, analytic_account_id)
        # value = {'credit': ..., 'debit': ..., 'amount_currency': ...}
        for donation_line in donation.line_ids:
            amount_total_company_cur += donation_line.amount_company_currency
            account_id = donation_line.product_id.property_account_income.id
            if not account_id:
                account_id = donation_line.product_id.categ_id.property_account_income_categ.id
            if not account_id:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing income account on product '%s' or on it's related product category") % donation_line.product_id.name)
            analytic_account_id = self._get_analytic_account_id(
                cr, uid, donation_line, account_id, context=context)
            if not currency_id:
                amount_currency = 0.0
            if donation_line.amount_company_currency > 0:
                credit = donation_line.amount_company_currency
                debit = 0
                if currency_id:
                    amount_currency = donation_line.amount * -1
            else:
                debit = donation_line.amount_company_currency * -1
                credit = 0
                if currency_id:
                    amount_currency = donation_line.amount

            #TODO Take into account the option group_invoice_lines ??
            if (account_id, analytic_account_id) in aml:
                aml[(account_id, analytic_account_id)]['credit'] += credit
                aml[(account_id, analytic_account_id)]['debit'] += debit
                aml[(account_id, analytic_account_id)]['amount_currency'] += amount_currency
            else:
                aml[(account_id, analytic_account_id)] = {
                    'credit': credit,
                    'debit': debit,
                    'amount_currency': amount_currency,
                    }

        for (account_id, analytic_account_id), content in aml.iteritems():
            movelines.append((0, 0, {
                'name': name,
                'credit': content['credit'],
                'debit': content['debit'],
                'account_id': account_id,
                'analytic_account_id': analytic_account_id,
                'partner_id': donation.partner_id.id,
                'currency_id': currency_id,
                'amount_currency': content['amount_currency'],
                }))

        # counter-part
        if amount_total_company_cur > 0:
            debit = amount_total_company_cur
            credit = 0
            if currency_id:
                total_amount_currency = donation.amount_total
        else:
            credit = amount_total_company_cur * -1
            debit = 0
            if currency_id:
                total_amount_currency = donation.amount_total * -1
        movelines.append(
            (0, 0, {
                'debit': debit,
                'credit': credit,
                'name': name,
                'account_id': donation.journal_id.default_debit_account_id.id,
                'partner_id': donation.partner_id.id,
                'currency_id': currency_id,
                'amount_currency': total_amount_currency,
            }))

        vals = {
            'journal_id': donation.journal_id.id,
            'date': donation.donation_date,
            'period_id': period_id,
            'ref': number,
            'line_id': movelines,
            }
        return vals

    def validate(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only one ID accepted'
        donation = self.browse(cr, uid, ids[0], context=context)

        if not donation.line_ids:
            raise orm.except_orm(
                _('Error:'),
                _('Cannot validate a donation without lines!'))

        if donation.check_total != donation.amount_total:
            raise orm.except_orm(
                _('Error:'),
                _("The amount of the donation (%s) is different from the sum of the donation lines (%s).")
                % (donation.check_total, donation.amount_total))

        donation_write_vals = {'state': 'done'}
        number = donation.number
        if not number:
            number = self.pool['ir.sequence'].next_by_code(
                cr, uid, 'donation.donation', context=context)
            donation_write_vals['number'] = number

        if donation.amount_total:
            move_vals = self._prepare_donation_move(
                cr, uid, donation, number, context=context)
            move_id = self.pool['account.move'].create(
                cr, uid, move_vals, context=context)

            self.pool['account.move'].post(cr, uid, [move_id], context=context)
            donation_write_vals['move_id'] = move_id

        self.write(cr, uid, donation.id, donation_write_vals, context=context)
        return True

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
        return True


class donation_line(orm.Model):
    _name = 'donation.line'
    _description = 'Donation Lines'
    _rec_name = 'product_id'

    def _compute_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount = line.quantity * line.unit_price
            company_cur_id = line.donation_id.company_id.currency_id.id
            donation_cur_id = line.donation_id.currency_id.id
            if company_cur_id == donation_cur_id:
                amount_company_currency = amount
            else:
                ctx_convert = context.copy()
                ctx_convert['date'] = line.donation_id.donation_date
                amount_company_currency = self.pool['res.currency'].compute(
                    cr, uid, donation_cur_id, company_cur_id, amount,
                    context=ctx_convert)
            res[line.id] = {
                'amount': amount,
                'amount_company_currency': amount_company_currency,
                }
        return res

    _columns = {
        'donation_id': fields.many2one(
            'donation.donation', 'Donation', ondelete='cascade'),
        'product_id': fields.many2one(
            'product.product', 'Product', required=True,
            domain=[('donation', '=', True)]),
        'quantity': fields.integer('Quantity'),
        'unit_price': fields.float(
            'Unit Price', digits_compute=dp.get_precision('Account')),
        'amount': fields.function(
            _compute_amount, multi="donline", type="float", string='Amount',
            digits_compute=dp.get_precision('Account'), store={
                'donation.line': (lambda self, cr, uid, ids, c={}: ids, ['quantity', 'unit_price'], 10),
                }),
        'amount_company_currency': fields.function(
            _compute_amount, multi="donline", type="float",
            string='Amount in Company Currency',
            digits_compute=dp.get_precision('Account'), store={
                'donation.line': (lambda self, cr, uid, ids, c={}: ids, ['quantity', 'unit_price'], 10),
                }),
        'analytic_account_id':  fields.many2one(
            'account.analytic.account', 'Analytic Account',
            domain=[('type', 'not in', ('view', 'template'))]),
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


    def _donation_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))
        # The current user may not have access rights for donations
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(partner.donation_ids)
        except:
            pass
        return res

    _columns = {
        'donation_ids': fields.one2many(
            'donation.donation', 'partner_id', 'Donations'),
        'donation_count': fields.function(
            _donation_count, string="# of Donations", type='integer'),
        }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'donation_ids': False,
        })
        return super(res_partner, self).copy(
            cr, uid, id, default=default, context=context)


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
