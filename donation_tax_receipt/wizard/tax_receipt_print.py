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


class DonationTaxReceiptPrint(models.TransientModel):
    _name = 'donation.tax.receipt.print'
    _description = 'Print Donation Tax Receipt'

    @api.model
    def _get_receipts(self):
        return self.env['donation.tax.receipt'].search(
            [('print_date', '=', False), ('create_uid', '=', self._uid)])

    receipt_ids = fields.Many2many(
        'donation.tax.receipt',
        column1='print_wizard_id', column2='receipt_id',
        string='Receipts To Print', default=_get_receipts)

    @api.multi
    def print_receipts(self):
        self.ensure_one()
        if not self.receipt_ids:
            raise Warning(
                _('There are no tax receipts to print.'))
        datas = {
            'model': 'donation.tax.receipt',
            'ids': self.receipt_ids.ids,
        }
        today = fields.Date.context_today(self)
        self.receipt_ids.write({'print_date': today})
        action = {
            'type': 'ir.actions.report.xml',
            'report_name': 'donation_tax_receipt.report_donationtaxreceipt',
            'data': datas,
            'datas': datas,  # for Aeroo
        }
        return action
