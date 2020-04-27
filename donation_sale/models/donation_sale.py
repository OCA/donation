# -*- coding: utf-8 -*-
# © 2016 La Cimade (http://www.lacimade.org/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
import logging

logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends(
        'invoice_line_ids.product_id', 'invoice_line_ids.price_unit',
        'invoice_line_ids.quantity')
    def _compute_tax_receipt_total(self):
        for inv in self:
            total = 0.0
            # Do not consider other currencies for tax receipts
            # because, for the moment, only very very few countries
            # accept tax receipts from other countries, and never in another
            # currency. If you know such cases, please tell us and we will
            # update the code of this module
            if inv.currency_id == inv.company_id.currency_id:
                for line in inv.invoice_line_ids:
                    if line.product_id.tax_receipt_ok:
                        # there are not sale taxes on tax receipts
                        total += line.quantity * line.price_unit
            inv.tax_receipt_total = total

    tax_receipt_id = fields.Many2one(
        'donation.tax.receipt', string='Tax Receipt', readonly=True,
        copy=False)
    tax_receipt_option = fields.Selection([
        ('none', 'None'),
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Tax Receipt Option', readonly=True,
        states={'draft': [('readonly', False)]}, index=True)
    tax_receipt_total = fields.Monetary(
        compute='_compute_tax_receipt_total', compute_sudo=True,
        string='Eligible Tax Receipt Sub-total',
        store=True, currency_field='company_currency_id', readonly=True)

    @api.onchange('partner_id')
    def donation_sale_change(self):
        if self.partner_id:
            self.tax_receipt_option = self.partner_id.tax_receipt_option
        else:
            self.tax_receipt_option = False

    def _prepare_each_tax_receipt(self):
        self.ensure_one()
        if self.payment_ids:
            date = self.payment_ids[0].payment_date
        else:
            date = self.date_invoice
        vals = {
            'company_id': self.company_id.id,
            'currency_id': self.company_currency_id.id,
            'donation_date': date,
            'date': date,
            'amount': self.tax_receipt_total,
            'type': 'each',
            'partner_id': self.commercial_partner_id.id,
        }
        return vals

    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        for inv in self:
            if inv.tax_receipt_id:
                raise UserError(_(
                    "You cannot cancel this invoice because "
                    "it is linked to the tax receipt %s. You should first "
                    "delete this tax receipt (but it may not be legally "
                    "allowed).")
                    % inv.tax_receipt_id.number)
        return res

    def unlink(self):
        for inv in self:
            if inv.tax_receipt_id:
                raise UserError(_(
                    "You cannot delete this invoice because it is linked to "
                    "the tax receipt %s") % inv.tax_receipt_id.number)
        return super(AccountInvoice, self).unlink()

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

    def action_invoice_paid(self):
        res = super(AccountInvoice, self).action_invoice_paid()
        dtro = self.env['donation.tax.receipt']
        to_gen_tax_receipt_invoices = self.filtered(
            lambda inv: inv.state == 'paid' and not inv.tax_receipt_id and
            inv.tax_receipt_option == 'each')
        for invoice in to_gen_tax_receipt_invoices:
            tax_receipt_amount = invoice.tax_receipt_total
            if float_is_zero(
                    tax_receipt_amount,
                    precision_rounding=invoice.currency_id.rounding):
                continue
            vals = invoice._prepare_each_tax_receipt()
            tax_receipt = dtro.with_context(
                ir_sequence_date=invoice.date_invoice).create(vals)
            invoice.tax_receipt_id = tax_receipt.id
            logger.debug(
                'Tax receipt ID %d generated for invoice ID %d partner %s',
                tax_receipt.id, invoice.id, invoice.commercial_partner_id.name)
        return res

    # TODO: remove this method and the one below
    # if the inherit of action_invoice_paid() works well
    def _generate_each_tax_receipt_from_invoices(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        dtro = self.env['donation.tax.receipt']
        for invoice in self:
            if invoice.tax_receipt_option != 'each':
                continue
            tax_receipt_amount = invoice.tax_receipt_total
            if float_is_zero(tax_receipt_amount, precision_digits=precision):
                continue
            partner = invoice.commercial_partner_id
            vals = invoice._prepare_each_tax_receipt()
            tax_receipt = dtro.with_context(
                ir_sequence_date=invoice.date_invoice).create(vals)
            invoice.tax_receipt_id = tax_receipt.id
            logger.debug(
                'Tax receipt ID %d generated for invoice ID %d partner %s',
                tax_receipt.id, invoice.id, partner.name)

    @api.model
    def _generate_each_tax_receipts(self):
        logger.info(
            "START to generate donation tax receipts from invoices "
            "(type='each')")
        invoices = self.env['account.invoice'].search([
            ('tax_receipt_option', '=', 'each'),
            ('tax_receipt_id', '=', False),
            ('tax_receipt_total', '!=', 0),
            ('company_id', '=', self.env.user.company_id.id),
            ('state', '=', 'paid'),
            ])
        invoices._generate_each_tax_receipt_from_invoices()
        logger.info(
            "END of the generation of donation tax receipts from invoices "
            "(type='each')")
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tax_receipt_ok = fields.Boolean(
        related='product_id.tax_receipt_ok', readonly=True, store=True,
        compute_sudo=True)

    @api.constrains('product_id', 'invoice_line_tax_ids')
    def donation_invoice_line_check(self):
        for line in self:
            if line.product_id.tax_receipt_ok and line.invoice_line_tax_ids:
                raise ValidationError(_(
                    "The invoice line '%s' has a donation product, "
                    "so it should not have taxes") % line.name)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tax_receipt_option = fields.Selection([
        ('none', 'None'),
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Tax Receipt Option', readonly=True,
        states={'draft': [('readonly', False)]})
    company_currency_id = fields.Many2one(
        related='company_id.currency_id', readonly=True)
    tax_receipt_total = fields.Monetary(
        compute='_compute_tax_receipt_total', compute_sudo=True,
        string='Eligible Tax Receipt Sub-total',
        store=True, currency_field='company_currency_id', readonly=True)

    @api.depends(
        'order_line.product_id', 'order_line.price_unit',
        'order_line.product_uom_qty')
    def _compute_tax_receipt_total(self):
        for sale in self:
            total = 0.0
            for line in sale.order_line:
                if line.product_id.tax_receipt_ok:
                    # there are not sale taxes on tax receipts
                    total += line.product_uom_qty * line.price_unit *\
                        (1 - (line.discount or 0.0) / 100.0)
            sale_currency = sale.currency_id.with_context(date=sale.date_order)
            total_cc = sale_currency.compute(
                total, sale.company_id.currency_id)
            sale.tax_receipt_total = total_cc

    @api.onchange('partner_id')
    def donation_sale_change(self):
        if self.partner_id:
            self.tax_receipt_option = self.partner_id.tax_receipt_option
        else:
            self.tax_receipt_option = False

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

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['tax_receipt_option'] = self.tax_receipt_option
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tax_receipt_ok = fields.Boolean(
        related='product_id.tax_receipt_ok', readonly=True, store=True,
        compute_sudo=True)
    # We don't handle in_kind donations via donation_sale for the moment
    # in_kind = fields.Boolean(
    #    related='product_id.in_kind_donation', readonly=True, store=True,
    #    string='In Kind')

    @api.constrains('product_id', 'tax_id')
    def donation_sale_line_check(self):
        for line in self:
            if line.product_id.tax_receipt_ok and line.tax_id:
                raise ValidationError(_(
                    "On the sale order '%s', the sale order line '%s' "
                    "has a donation product, so it should not have taxes")
                    % (line.order_id.name, line.name))


class DonationTaxReceipt(models.Model):
    _inherit = 'donation.tax.receipt'

    invoice_ids = fields.One2many(
        'account.invoice', 'tax_receipt_id', string='Related Invoices')

    @api.model
    def update_tax_receipt_annual_dict(
            self, tax_receipt_annual_dict, start_date, end_date,
            precision_rounding):
        super(DonationTaxReceipt, self).update_tax_receipt_annual_dict(
            tax_receipt_annual_dict, start_date, end_date, precision_rounding)
        invoices = self.env['account.invoice'].search([
            ('date_invoice', '>=', start_date),
            ('date_invoice', '<=', end_date),
            ('tax_receipt_option', '=', 'annual'),
            ('tax_receipt_id', '=', False),
            ('tax_receipt_total', '!=', 0),
            ('company_id', '=', self.env.user.company_id.id),
            ('state', 'in', ('open', 'paid')),
            ])
        for invoice in invoices:
            tax_receipt_amount = invoice.tax_receipt_total
            if float_is_zero(
                    tax_receipt_amount, precision_rounding=precision_rounding):
                continue
            partner = invoice.commercial_partner_id
            if partner not in tax_receipt_annual_dict:
                tax_receipt_annual_dict[partner] = {
                    'amount': tax_receipt_amount,
                    'extra_vals': {
                        'donation_ids': [(6, 0, [invoice.id])]},
                    }
            else:
                tax_receipt_annual_dict[partner]['amount'] +=\
                    tax_receipt_amount
                tax_receipt_annual_dict[partner]['extra_vals'][
                    'donation_ids'][0][2].append(invoice.id)
