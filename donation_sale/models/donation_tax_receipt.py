# Copyright 2016-2021 La Cimade (http://www.lacimade.org/)
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class DonationTaxReceipt(models.Model):
    _inherit = 'donation.tax.receipt'

    invoice_ids = fields.One2many(
        'account.move',
        'tax_receipt_id',
        string='Related Invoices'
    )

    @api.model
    def update_tax_receipt_annual_dict(
            self, tax_receipt_annual_dict, start_date, end_date,
            company):
        super().update_tax_receipt_annual_dict(
            tax_receipt_annual_dict, start_date, end_date, company)
        moves = self.env['account.move'].search([
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('move_type', '=', 'out_invoice'),
            ('tax_receipt_option', '=', 'annual'),
            ('tax_receipt_id', '=', False),
            ('tax_receipt_total', '!=', 0),
            ('company_id', '=', company.id),
            ('state', '=', 'posted'),
            ])
        for move in moves:
            tax_receipt_amount = move.tax_receipt_total
            if company.currency_id.is_zero(tax_receipt_amount):
                continue
            partner = move.commercial_partner_id
            if partner not in tax_receipt_annual_dict:
                tax_receipt_annual_dict[partner] = {
                    'amount': tax_receipt_amount,
                    'extra_vals': {
                        'invoice_ids': [(6, 0, [move.id])]},
                    }
            else:
                tax_receipt_annual_dict[partner]['amount'] +=\
                    tax_receipt_amount
                tax_receipt_annual_dict[partner]['extra_vals'][
                    'invoice_ids'][0][2].append(move.id)
