# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
from odoo.addons.account import _auto_install_l10n


class DonationDonation(models.Model):
    _name = 'donation.donation'
    _description = 'Donation'
    _order = 'id desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread']

    @api.multi
    @api.depends(
        'line_ids.unit_price', 'line_ids.quantity',
        'line_ids.product_id', 'donation_date', 'currency_id', 'company_id')
    def _compute_total(self):
        for donation in self:
            total = tax_receipt_total = 0.0
            donation_currency = donation.currency_id
            for line in donation.line_ids:
                line_total = line.quantity * line.unit_price
                total += line_total
                # products may be per company -> sudo()
                if line.sudo().product_id.tax_receipt_ok:
                    tax_receipt_total += line_total

            donation.amount_total = total
            donation_currency =\
                donation.currency_id.with_context(date=donation.donation_date)
            company_currency = donation.company_id.currency_id
            total_company_currency = donation_currency.compute(
                total, company_currency)
            tax_receipt_total_cc = donation_currency.compute(
                tax_receipt_total, company_currency)
            donation.amount_total_company_currency = total_company_currency
            donation.tax_receipt_total = tax_receipt_total_cc

    # We don't want a depends on partner_id.country_id, because if the partner
    # moves to another country, we want to keep the old country for
    # past donations to have good statistics
    @api.multi
    @api.depends('partner_id')
    def _compute_country_id(self):
        # Use sudo() to by-pass record rules, because the same partner
        # can have donations in several companies
        for donation in self:
            donation.sudo().country_id = donation.partner_id.country_id

    @api.model
    def _default_currency(self):
        company = self.env['res.company']._company_default_get(
            'donation.donation')
        return company.currency_id

    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        states={'done': [('readonly', True)]},
        track_visibility='onchange', ondelete='restrict',
        default=_default_currency)
    partner_id = fields.Many2one(
        'res.partner', string='Donor', required=True, index=True,
        states={'done': [('readonly', True)]},
        track_visibility='onchange', ondelete='restrict')
    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string='Parent Donor', readonly=True, store=True, index=True)
    # country_id is here to have stats per country
    # WARNING : I can't put a related field, because when someone
    # writes on the country_id of a partner, it will trigger a write
    # on all it's donations, including donations in other companies
    # which will be blocked by the record rule
    country_id = fields.Many2one(
        'res.country', string='Country', compute='_compute_country_id',
        store=True, readonly=True, copy=False)
    check_total = fields.Monetary(
        string='Check Amount',
        states={'done': [('readonly', True)]}, currency_field='currency_id',
        track_visibility='onchange')
    amount_total = fields.Monetary(
        compute='_compute_total', string='Amount Total',
        currency_field='currency_id', store=True,
        readonly=True, track_visibility='onchange')
    amount_total_company_currency = fields.Monetary(
        compute='_compute_total', string='Amount Total in Company Currency',
        currency_field='company_currency_id',
        store=True, readonly=True)
    donation_date = fields.Date(
        string='Donation Date', required=True,
        states={'done': [('readonly', True)]}, index=True,
        track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        states={'done': [('readonly', True)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'donation.donation'))
    line_ids = fields.One2many(
        'donation.line', 'donation_id', string='Donation Lines',
        states={'done': [('readonly', True)]}, copy=True)
    move_id = fields.Many2one(
        'account.move', string='Account Move', readonly=True, copy=False)
    number = fields.Char(
        related='move_id.name', readonly=True, size=64,
        store=True, string='Donation Number')
    journal_id = fields.Many2one(
        'account.journal', string='Payment Method', required=True,
        domain=[
            ('type', 'in', ('bank', 'cash')),
            ('allow_donation', '=', True)],
        states={'done': [('readonly', True)]},
        track_visibility='onchange',
        default=lambda self: self.env.user.context_donation_journal_id)
    payment_ref = fields.Char(
        string='Payment Reference', size=32,
        states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='State', readonly=True, copy=False, default='draft',
        index=True, track_visibility='onchange')
    company_currency_id = fields.Many2one(
        related='company_id.currency_id', string="Company Currency",
        readonly=True, store=True)
    campaign_id = fields.Many2one(
        'donation.campaign', string='Donation Campaign',
        track_visibility='onchange', ondelete='restrict',
        default=lambda self: self.env.user.context_donation_campaign_id)
    display_name = fields.Char(
        string='Display Name', compute='_compute_display_name_field',
        readonly=True)
    tax_receipt_id = fields.Many2one(
        'donation.tax.receipt', string='Tax Receipt', readonly=True,
        copy=False, track_visibility='onchange')
    tax_receipt_option = fields.Selection([
        ('none', 'None'),
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Tax Receipt Option', states={'done': [('readonly', True)]},
        index=True, track_visibility='onchange')
    tax_receipt_total = fields.Monetary(
        compute='_compute_total', string='Tax Receipt Eligible Amount',
        store=True, readonly=True, currency_field='company_currency_id',
        help="Eligible Tax Receipt Sub-total in Company Currency")

    @api.multi
    @api.constrains('donation_date')
    def _check_donation_date(self):
        for donation in self:
            if donation.donation_date > fields.Date.context_today(self):
                # TODO No error pop-up to user : Odoo 9 BUG ?
                raise ValidationError(_(
                    'The date of the donation of %s should be today '
                    'or in the past, not in the future!')
                    % donation.partner_id.name)

    @api.multi
    def _prepare_each_tax_receipt(self):
        self.ensure_one()
        vals = {
            'company_id': self.company_id.id,
            'currency_id': self.company_currency_id.id,
            'donation_date': self.donation_date,
            'amount': self.tax_receipt_total,
            'type': 'each',
            'partner_id': self.commercial_partner_id.id,
        }
        return vals

    @api.multi
    def _prepare_move_line_name(self):
        self.ensure_one()
        name = _('Donation of %s') % self.partner_id.name
        return name

    @api.multi
    def _prepare_counterpart_move_line(
            self, name, amount_total_company_cur, total_amount_currency,
            currency_id):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Account')
        if float_compare(
                amount_total_company_cur, 0, precision_digits=precision) == 1:
            debit = amount_total_company_cur
            credit = 0
            total_amount_currency = self.amount_total
        else:
            credit = amount_total_company_cur * -1
            debit = 0
            total_amount_currency = self.amount_total * -1
        vals = {
            'debit': debit,
            'credit': credit,
            'name': name,
            'account_id': self.journal_id.default_debit_account_id.id,
            'partner_id': self.commercial_partner_id.id,
            'currency_id': currency_id,
            'amount_currency': (
                currency_id and total_amount_currency or 0.0),
            }
        return vals

    @api.multi
    def _prepare_donation_move(self):
        self.ensure_one()
        if not self.journal_id.default_debit_account_id:
            raise UserError(
                _("Missing Default Debit Account on journal '%s'.")
                % self.journal_id.name)

        movelines = []
        if self.company_id.currency_id.id != self.currency_id.id:
            currency_id = self.currency_id.id
        else:
            currency_id = False
        # Note : we can have negative donations for donors that use direct
        # debit when their direct debit rejected by the bank
        amount_total_company_cur = 0.0
        total_amount_currency = 0.0
        name = self._prepare_move_line_name()

        aml = {}
        # key = (account_id, analytic_account_id)
        # value = {'credit': ..., 'debit': ..., 'amount_currency': ...}
        precision = self.env['decimal.precision'].precision_get('Account')
        for donation_line in self.line_ids:
            if donation_line.in_kind:
                continue
            amount_total_company_cur += donation_line.amount_company_currency
            account_id = donation_line.product_id.property_account_income_id.id
            if not account_id:
                account_id = donation_line.product_id.categ_id.\
                    property_account_income_categ_id.id
            if not account_id:
                raise UserError(
                    _("Missing income account on product '%s' or on it's "
                        "related product category")
                    % donation_line.product_id.name)
            analytic_account_id = donation_line.get_analytic_account_id()
            amount_currency = 0.0
            if float_compare(
                    donation_line.amount_company_currency, 0,
                    precision_digits=precision) == 1:
                credit = donation_line.amount_company_currency
                debit = 0
                amount_currency = donation_line.amount * -1
            else:
                debit = donation_line.amount_company_currency * -1
                credit = 0
                amount_currency = donation_line.amount

            # TODO Take into account the option group_invoice_lines ?
            if (account_id, analytic_account_id) in aml:
                aml[(account_id, analytic_account_id)]['credit'] += credit
                aml[(account_id, analytic_account_id)]['debit'] += debit
                aml[(account_id, analytic_account_id)]['amount_currency'] \
                    += amount_currency
            else:
                aml[(account_id, analytic_account_id)] = {
                    'credit': credit,
                    'debit': debit,
                    'amount_currency': amount_currency,
                    }

        if not aml:  # for full in-kind donation
            return False

        for (account_id, analytic_account_id), content in aml.iteritems():
            movelines.append((0, 0, {
                'name': name,
                'credit': content['credit'],
                'debit': content['debit'],
                'account_id': account_id,
                'analytic_account_id': analytic_account_id,
                'partner_id': self.commercial_partner_id.id,
                'currency_id': currency_id,
                'amount_currency': (
                    currency_id and content['amount_currency'] or 0.0),
                }))

        # counter-part
        ml_vals = self._prepare_counterpart_move_line(
            name, amount_total_company_cur, total_amount_currency,
            currency_id)
        movelines.append((0, 0, ml_vals))

        vals = {
            'journal_id': self.journal_id.id,
            'date': self.donation_date,
            'ref': self.payment_ref,
            'line_ids': movelines,
            }
        return vals

    @api.multi
    def validate(self):
        check_total = self.env['res.users'].has_group(
            'donation.group_donation_check_total')
        for donation in self:
            if not donation.line_ids:
                raise UserError(_(
                    "Cannot validate the donation of %s because it doesn't "
                    "have any lines!") % donation.partner_id.name)

            if float_is_zero(
                    donation.amount_total,
                    precision_rounding=donation.currency_id.rounding):
                raise UserError(_(
                    "Cannot validate the donation of %s because the "
                    "total amount is 0 !") % donation.partner_id.name)

            if donation.state != 'draft':
                raise UserError(_(
                    "Cannot validate the donation of %s because it is not "
                    "in draft state.") % donation.partner_id.name)

            if check_total and float_compare(
                    donation.check_total, donation.amount_total,
                    precision_rounding=donation.currency_id.rounding):
                raise UserError(_(
                    "The amount of the donation of %s (%s) is different "
                    "from the sum of the donation lines (%s).") % (
                    donation.partner_id.name, donation.check_total,
                    donation.amount_total))

            vals = {'state': 'done'}

            if not float_is_zero(
                    donation.amount_total,
                    precision_rounding=donation.currency_id.rounding):
                move_vals = donation._prepare_donation_move()
                # when we have a full in-kind donation: no account move
                if move_vals:
                    move = self.env['account.move'].create(move_vals)
                    move.post()
                    vals['move_id'] = move.id
                else:
                    donation.message_post(_(
                        'Full in-kind donation: no account move generated'))

            receipt = donation.generate_each_tax_receipt()
            if receipt:
                vals['tax_receipt_id'] = receipt.id

            donation.write(vals)
        return

    @api.multi
    def generate_each_tax_receipt(self):
        self.ensure_one()
        receipt = False
        if (
                self.tax_receipt_option == 'each' and
                not self.tax_receipt_id and
                not float_is_zero(
                    self.tax_receipt_total,
                    precision_rounding=self.company_currency_id.rounding)):
            receipt_vals = self._prepare_each_tax_receipt()
            receipt = self.env['donation.tax.receipt'].create(receipt_vals)
        return receipt

    @api.multi
    def save_default_values(self):
        self.ensure_one()
        self.env.user.write({
            'context_donation_journal_id': self.journal_id.id,
            'context_donation_campaign_id': self.campaign_id.id,
            })

    @api.multi
    def done2cancel(self):
        '''from Done state to Cancel state'''
        for donation in self:
            if donation.tax_receipt_id:
                raise UserError(_(
                    "You cannot cancel this donation because "
                    "it is linked to the tax receipt %s. You should first "
                    "delete this tax receipt (but it may not be legally "
                    "allowed).")
                    % donation.tax_receipt_id.number)
            if donation.move_id:
                donation.move_id.button_cancel()
                donation.move_id.unlink()
            donation.state = 'cancel'

    @api.multi
    def cancel2draft(self):
        '''from Cancel state to Draft state'''
        for donation in self:
            if donation.move_id:
                raise UserError(_(
                    "A cancelled donation should not be linked to "
                    "an account move"))
            if donation.tax_receipt_id:
                raise UserError(_(
                    "A cancelled donation should not be linked to "
                    "a tax receipt"))
            donation.state = 'draft'

    @api.multi
    def unlink(self):
        for donation in self:
            if donation.state == 'done':
                raise UserError(_(
                    "The donation '%s' is in Done state, so you cannot "
                    "delete it.") % donation.display_name)
            if donation.move_id:
                raise UserError(_(
                    "The donation '%s' is linked to an account move, "
                    "so you cannot delete it.") % donation.display_name)
            if donation.tax_receipt_id:
                raise UserError(_(
                    "The donation '%s' is linked to the tax receipt %s, "
                    "so you cannot delete it.")
                    % (donation.display_name, donation.tax_receipt_id.number))
        return super(DonationDonation, self).unlink()

    @api.multi
    @api.depends('state', 'partner_id', 'move_id')
    def _compute_display_name_field(self):
        for donation in self:
            partner = donation.sudo().partner_id
            if donation.state == 'draft':
                name = _('Draft Donation of %s') % partner.name
            elif donation.state == 'cancel':
                name = _('Cancelled Donation of %s') % partner.name
            else:
                name = donation.number
            donation.display_name = name

    @api.onchange('partner_id')
    def partner_id_change(self):
        if self.partner_id:
            self.tax_receipt_option = self.partner_id.tax_receipt_option

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

    @api.model
    def auto_install_l10n(self):
        """Helper function for calling a method that is not accessible directly
        from XML data.
        """
        _auto_install_l10n(self.env.cr, None)


class DonationLine(models.Model):
    _name = 'donation.line'
    _description = 'Donation Lines'
    _rec_name = 'product_id'

    @api.multi
    @api.depends(
        'unit_price', 'quantity', 'product_id', 'donation_id.currency_id',
        'donation_id.donation_date', 'donation_id.company_id')
    def _compute_amount(self):
        for line in self:
            amount = line.quantity * line.unit_price
            line.amount = amount
            donation_currency = line.donation_id.currency_id.with_context(
                date=line.donation_id.donation_date)
            amount_company_currency = donation_currency.compute(
                amount, line.donation_id.company_id.currency_id)
            tax_receipt_amount_cc = 0.0
            if line.sudo().product_id.tax_receipt_ok:
                tax_receipt_amount_cc = amount_company_currency
            line.amount_company_currency = amount_company_currency
            line.tax_receipt_amount = tax_receipt_amount_cc

    donation_id = fields.Many2one(
        'donation.donation', string='Donation', ondelete='cascade')
    currency_id = fields.Many2one(
        'res.currency', related='donation_id.currency_id', readonly=True)
    company_currency_id = fields.Many2one(
        'res.currency', related='donation_id.company_id.currency_id',
        readonly=True)
    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        domain=[('donation', '=', True)], ondelete='restrict')
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Monetary(
        string='Unit Price', currency_field='currency_id')
    amount = fields.Monetary(
        compute='_compute_amount', string='Amount',
        currency_field='currency_id', store=True, readonly=True)
    amount_company_currency = fields.Monetary(
        compute='_compute_amount',
        string='Amount in Company Currency',
        currency_field='company_currency_id', store=True, readonly=True)
    tax_receipt_amount = fields.Monetary(
        compute='_compute_amount',
        string='Tax Receipt Eligible Amount',
        currency_field='company_currency_id', store=True, readonly=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        ondelete='restrict')
    sequence = fields.Integer('Sequence')
    # for the fields tax_receipt_ok and in_kind, we made an important change
    # between v8 and v9: in v8, it was a reglar field set by an onchange
    # in v9, it is a related stored field
    tax_receipt_ok = fields.Boolean(
        related='product_id.tax_receipt_ok', readonly=True, store=True)
    in_kind = fields.Boolean(
        related='product_id.in_kind_donation', readonly=True, store=True,
        string='In Kind')

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            # We should change that one day...
            if self.product_id.list_price:
                self.unit_price = self.product_id.list_price

    @api.model
    def get_analytic_account_id(self):
        return self.analytic_account_id.id or False


class DonationTaxReceipt(models.Model):
    _inherit = 'donation.tax.receipt'

    donation_ids = fields.One2many(
        'donation.donation', 'tax_receipt_id', string='Related Donations')

    @api.model
    def update_tax_receipt_annual_dict(
            self, tax_receipt_annual_dict, start_date, end_date,
            precision_rounding):
        super(DonationTaxReceipt, self).update_tax_receipt_annual_dict(
            tax_receipt_annual_dict, start_date, end_date, precision_rounding)
        donations = self.env['donation.donation'].search([
            ('donation_date', '>=', start_date),
            ('donation_date', '<=', end_date),
            ('tax_receipt_option', '=', 'annual'),
            ('tax_receipt_id', '=', False),
            ('tax_receipt_total', '!=', 0),
            ('company_id', '=', self.env.user.company_id.id),
            ('state', '=', 'done'),
            ])
        for donation in donations:
            tax_receipt_amount = donation.tax_receipt_total
            if float_is_zero(
                    tax_receipt_amount, precision_rounding=precision_rounding):
                continue
            partner = donation.commercial_partner_id
            if partner not in tax_receipt_annual_dict:
                tax_receipt_annual_dict[partner] = {
                    'amount': tax_receipt_amount,
                    'extra_vals': {
                        'donation_ids': [(6, 0, [donation.id])]},
                    }
            else:
                tax_receipt_annual_dict[partner]['amount'] +=\
                    tax_receipt_amount
                tax_receipt_annual_dict[partner]['extra_vals'][
                    'donation_ids'][0][2].append(donation.id)
