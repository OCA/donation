# Copyright 2016-2021 La Cimade (http://www.lacimade.org/)
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_line_ids.price_subtotal', 'currency_id', 'invoice_line_ids.product_id')
    def _compute_tax_receipt_total(self):
        for move in self:
            total = 0.0
            if move.move_type == 'out_invoice':
                for line in move.invoice_line_ids:
                    if not line.display_type and line.product_id.tax_receipt_ok:
                        total += move.currency_id._convert(line.price_subtotal, move.company_id.currency_id, move.company_id, move.invoice_date or fields.Date.context_today(self))
            move.tax_receipt_total = total

    tax_receipt_id = fields.Many2one(
        'donation.tax.receipt',
        string='Tax Receipt',
        readonly=True,
        copy=False,
        check_company=True,
    )
    tax_receipt_option = fields.Selection(
        [('none', 'None'),
         ('each', 'For Each Donation'),
         ('annual', 'Annual Tax Receipt')],
        string='Tax Receipt Option',
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True
    )
    tax_receipt_total = fields.Monetary(
        compute='_compute_tax_receipt_total',
        string='Eligible Tax Receipt Sub-total',
        store=True,
        currency_field='company_currency_id',
    )

    @api.onchange('partner_id')
    def donation_sale_change(self):
        if self.partner_id:
            self.tax_receipt_option = self.partner_id.commercial_partner_id.tax_receipt_option
        else:
            self.tax_receipt_option = False

    def _prepare_each_tax_receipt(self):
        self.ensure_one()
        date = self.invoice_date
        for payment in self._get_reconciled_info_JSON_values():
            if payment['date'] > date:
                date = payment['date']
        vals = {
            'company_id': self.company_id.id,
            'currency_id': self.company_id.currency_id.id,
            'donation_date': date,
            'date': date,
            'amount': self.tax_receipt_total,
            'type': 'each',
            'partner_id': self.commercial_partner_id.id,
        }
        return vals

    def button_cancel(self):
        for move in self:
            if move.tax_receipt_id:
                raise UserError(_(
                    "You cannot cancel the invoice '%s' because "
                    "it is linked to the tax receipt %s. You should first "
                    "delete this tax receipt (but it may not be legally "
                    "allowed).")
                    % (move.display_name, move.tax_receipt_id.number))
        return super().button_cancel()

    def unlink(self):
        for move in self:
            if move.tax_receipt_id:
                raise UserError(_(
                    "You cannot delete the invoice '%s' because it is linked to "
                    "the tax receipt %s.") % (move.display_name, move.tax_receipt_id.number))
        return super().unlink()

    @api.onchange('tax_receipt_option')
    def tax_receipt_option_change(self):
        res = {}
        if (
                self.commercial_partner_id and
                self.commercial_partner_id.tax_receipt_option == 'annual' and
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

    def _generate_each_tax_receipt_from_invoices(self):
        dtro = self.env['donation.tax.receipt']
        for move in self:
            if move.tax_receipt_option != 'each':
                continue
            tax_receipt_amount = move.tax_receipt_total
            if move.company_id.currency_id.is_zero(tax_receipt_amount):
                continue
            partner = move.commercial_partner_id
            vals = move._prepare_each_tax_receipt()
            tax_receipt = dtro.with_context(
                ir_sequence_date=move.invoice_date).create(vals)
            move.write({'tax_receipt_id': tax_receipt.id})
            logger.debug(
                'Tax receipt ID %d generated for move ID %d partner %s',
                tax_receipt.id, move.id, partner.display_name)

    @api.model
    def _generate_each_tax_receipts(self):
        logger.info(
            "START to generate donation tax receipts from invoices "
            "(type='each')")
        for company in self.env['res.company'].search([]):
            moves = self.search([
                ('move_type', '=', 'out_invoice'),
                ('tax_receipt_option', '=', 'each'),
                ('tax_receipt_id', '=', False),
                ('tax_receipt_total', '!=', 0),
                ('company_id', '=', company.id),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid'),
                ])
            moves._generate_each_tax_receipt_from_invoices()
        logger.info(
            "END of the generation of donation tax receipts from invoices "
            "(type='each')")
        return True


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_receipt_ok = fields.Boolean(
        related='product_id.tax_receipt_ok',
        store=True,
    )

    @api.constrains('product_id', 'tax_ids')
    def donation_invoice_line_check(self):
        for line in self:
            if line.product_id and line.product_id.tax_receipt_ok and line.tax_ids:
                raise ValidationError(_(
                    "The invoice line '%s' has a donation product, "
                    "so it should not have taxes.") % line.display_name)
