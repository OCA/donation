# © 2016 La Cimade (http://www.lacimade.org/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_is_zero
import logging

logger = logging.getLogger(__name__)


class DonationTaxReceipt(models.Model):
    _inherit = 'donation.tax.receipt'

    invoice_ids = fields.One2many(
        'account.invoice',
        'tax_receipt_id',
        string='Related Invoices'
    )

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
