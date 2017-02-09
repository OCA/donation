# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


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
    def _prepare_annual_tax_receipt(self, partner_id, partner_dict):
        vals = {
            'company_id': self.env.user.company_id.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'amount': partner_dict['amount'],
            'type': 'annual',
            'partner_id': partner_id,
            'date': self.end_date,
            'donation_date': self.end_date,
            'donation_ids': [(6, 0, partner_dict['donation_ids'])],
        }
        return vals

    @api.multi
    def generate_annual_receipts(self):
        self.ensure_one()
        logger.info(
            'START to generate annual fiscal receipts from %s to %s',
            self.start_date, self.end_date)
        donations = self.env['donation.donation'].search([
            ('donation_date', '>=', self.start_date),
            ('donation_date', '<=', self.end_date),
            ('tax_receipt_option', '=', 'annual'),
            ('tax_receipt_id', '=', False),
            ('tax_receipt_total', '!=', 0),
            ('company_id', '=', self.env.user.company_id.id),
            ('state', '=', 'done'),
            ])
        tax_receipt_annual = {}
        # {partner_id: {
        #       'amount': amount,
        #       'donation_ids': [donation1_id, donation2_id]}}
        for donation in donations:
            partner_id = donation.partner_id.id
            tax_receipt_amount = donation.tax_receipt_total
            if partner_id not in tax_receipt_annual:
                tax_receipt_annual[partner_id] = {
                    'amount': tax_receipt_amount,
                    'donation_ids': [donation.id],
                }
            else:
                tax_receipt_annual[partner_id]['amount'] +=\
                    tax_receipt_amount
                tax_receipt_annual[partner_id]['donation_ids']\
                    .append(donation.id)

        tax_receipt_ids = []
        for partner_id, partner_dict in tax_receipt_annual.iteritems():
            vals = self._prepare_annual_tax_receipt(partner_id, partner_dict)
            # Block if the partner already has an annual fiscal receipt
            # or an each fiscal receipt
            already_tax_receipts = \
                self.env['donation.tax.receipt'].search([
                    ('donation_date', '<=', self.end_date),
                    ('donation_date', '>=', self.start_date),
                    ('company_id', '=', vals['company_id']),
                    ('partner_id', '=', vals['partner_id']),
                    ])
            if already_tax_receipts:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                raise Warning(
                    _("The Donor '%s' already has a tax receipt "
                        "in this timeframe: %s dated %s.")
                    % (partner.name, already_tax_receipts[0].number,
                        already_tax_receipts[0].date))
            tax_receipt = self.env['donation.tax.receipt'].create(vals)
            tax_receipt_ids.append(tax_receipt.id)
            logger.info('Tax receipt %s generated', tax_receipt.number)
        logger.info(
            '%d annual fiscal receipts generated', len(tax_receipt_ids))
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
