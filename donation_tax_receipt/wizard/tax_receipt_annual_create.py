# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for OpenERP
#    Copyright (C) 2014 Artisanat Monastique de Provence
#       (http://www.barroux.org)
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
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class tax_receipt_annual_create(orm.TransientModel):
    _name = 'tax.receipt.annual.create'
    _description = 'Generate Annual Tax Receipt'

    _columns = {
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
    }

    def _default_end_date(self, cr, uid, context=None):
        end_date = datetime(datetime.today().year - 1, 12, 31)
        return datetime.strftime(end_date, DEFAULT_SERVER_DATE_FORMAT)

    def _default_start_date(self, cr, uid, context=None):
        start_date = datetime(datetime.today().year - 1, 1, 1)
        return datetime.strftime(start_date, DEFAULT_SERVER_DATE_FORMAT)

    _defaults = {
        'start_date': _default_start_date,
        'end_date': _default_end_date,
    }

    def _prepare_annual_tax_receipt(
            self, cr, uid, company_id, partner_id, partner_dict,
            wizard, context=None):
        vals = {
            'company_id': company_id,
            'amount': partner_dict['amount'],
            'type': 'annual',
            'partner_id': partner_id,
            'date': wizard.end_date,
            'donation_date': wizard.end_date,
            'donation_ids': [(6, 0, partner_dict['donation_ids'])],
            'number': self.pool['donation.tax.receipt'].get_tax_receipt_number(
                cr, uid, wizard.end_date, context=context),
        }
        print "valssssss=", vals
        return vals

    def generate_annual_receipts(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only 1 ID for a wizard'
        wizard = self.browse(cr, uid, ids[0], context=context)
        donation_ids = self.pool['donation.donation'].search(
            cr, uid, [
                ('donation_date', '>=', wizard.start_date),
                ('donation_date', '<=', wizard.end_date),
                ('tax_receipt_option', '=', 'annual'),
                ('tax_receipt_id', '=', False),
                ('tax_receipt_total', '!=', 0),
                ], context=context)
        print "donation_ids=", donation_ids
        donations = self.pool['donation.donation'].read(
            cr, uid, donation_ids,
            ['tax_receipt_total', 'partner_id', 'company_id'],
            context=context)
        tax_receipt_annual = {}
        # {company_id: {
        #    partner_id: {
        #       'amount': amount,
        #       'donation_ids': [donation1_id, donation2_id]}}
        for donation in donations:
            company_id = donation['company_id'][0]
            partner_id = donation['partner_id'][0]
            donation_id = donation['id']
            tax_receipt_amount = donation['tax_receipt_total']
            if company_id not in tax_receipt_annual:
                tax_receipt_annual[company_id] = {}
            if partner_id not in tax_receipt_annual[company_id]:
                tax_receipt_annual[company_id][partner_id] = {
                    'amount': tax_receipt_amount,
                    'donation_ids': [donation_id],
                }
            else:
                tax_receipt_annual[company_id][partner_id]['amount'] +=\
                    tax_receipt_amount
                tax_receipt_annual[company_id][partner_id]['donation_ids']\
                    .append(donation_id)

        print "tax_receipt_annual=", tax_receipt_annual
        tax_receipt_ids = []
        for company_id, partners_dict in tax_receipt_annual.iteritems():
            for partner_id, partner_dict in partners_dict.iteritems():
                vals = self._prepare_annual_tax_receipt(
                    cr, uid, company_id, partner_id, partner_dict,
                    wizard, context=context)
                # Block if the partner already has an annual fiscal receipt
                # or an each fiscal receipt
                already_tax_receipt_ids = \
                    self.pool['donation.tax.receipt'].search(
                        cr, uid, [
                            ('date', '<=', wizard.end_date),
                            ('date', '>=', wizard.start_date),
                            ('company_id', '=', vals['company_id']),
                            ('partner_id', '=', vals['partner_id']),
                            ], context=context)
                if already_tax_receipt_ids:
                    partner = self.pool['res.partner'].browse(
                        cr, uid, vals['partner_id'], context=context)
                    company = self.pool['res.company'].browse(
                        cr, uid, vals['company_id'], context=context)
                    raise orm.except_orm(
                        _('Error:'),
                        _("The Donor '%s' already has a tax receipt in the "
                            "company '%s' in this timeframe.")
                        % (partner.name, company.name))
                tax_receipt_id = self.pool['donation.tax.receipt'].create(
                    cr, uid, vals, context=context)
                tax_receipt_ids.append(tax_receipt_id)
        print "tax_receipt_ids=", tax_receipt_ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Tax Receipts',
            'res_model': 'donation.tax.receipt',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'nodestroy': False,
            'target': 'current',
            'domain': [('id', 'in', tax_receipt_ids)],
            }
        return action
