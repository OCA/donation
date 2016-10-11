# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError
from datetime import datetime


class TaxReceiptAnnualCreate(models.TransientModel):
    _name = 'tax.receipt.annual.create'
    _description = 'Generate Annual Tax Receipt'

    @api.model
    def _default_end_date(self):
        return datetime(datetime.today().year - 1, 12, 31)

    @api.model
    def _default_start_date(self):
        return datetime(datetime.today().year - 1, 1, 1)

    start_date = fields.Date(
        'Start Date', required=True, default=_default_start_date)
    end_date = fields.Date(
        'End Date', required=True, default=_default_end_date)

    @api.model
    def _prepare_annual_tax_receipt(self, partner, partner_dict):
        vals = {
            'company_id': self.env.user.company_id.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'amount': partner_dict['amount'],
            'type': 'annual',
            'partner_id': partner.id,
            'date': self.end_date,
            'donation_date': self.end_date,
        }
        # designed to add add O2M fields donation_ids and invoice_ids
        vals.update(partner_dict['extra_vals'])
        return vals

    @api.multi
    def generate_annual_receipts(self):
        self.ensure_one()
        dtro = self.env['donation.tax.receipt']
        tax_receipt_annual_dict = {}
        precision = self.env['decimal.precision'].precision_get('Account')
        self.env['donation.tax.receipt'].update_tax_receipt_annual_dict(
            tax_receipt_annual_dict, self.start_date, self.end_date,
            precision)
        # {commercial_partner: {
        #       'amount': amount,
        #       'extra_vals': {donation_ids': [donation1_id, donation2_id]}}}
        tax_receipt_ids = []
        existing_annual_receipts = dtro.search([
            ('date', '<=', self.end_date),
            ('date', '>=', self.start_date),
            ('company_id', '=', self.env.user.company_id.id),
            ('type', '=', 'annual'),
            ])
        existing_annual_receipts_dict = {}
        for receipt in existing_annual_receipts:
            existing_annual_receipts_dict[receipt.partner_id] = receipt

        for partner, partner_dict in tax_receipt_annual_dict.iteritems():
            # Block if the partner already has an annual tax receipt
            if partner in existing_annual_receipts_dict:
                existing_receipt = existing_annual_receipts_dict[partner]
                raise UserError(_(
                    "The Donor '%s' already has an annual tax receipt "
                    "in this timeframe: %s dated %s.")
                    % (partner.name, existing_receipt.number,
                        existing_receipt.date))
            vals = self._prepare_annual_tax_receipt(partner, partner_dict)
            tax_receipt = dtro.create(vals)
            tax_receipt_ids.append(tax_receipt.id)
        if not tax_receipt_ids:
            raise UserError(_("No annual tax receipt to generate"))
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Tax Receipts',
            'res_model': 'donation.tax.receipt',
            'view_mode': 'tree,form,graph',
            'nodestroy': False,
            'target': 'current',
            'domain': [('id', 'in', tax_receipt_ids)],
            }
        return action
