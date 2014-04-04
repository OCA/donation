# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for OpenERP
#    Copyright (C) 2014 Artisanat Monastique de Provence (http://www.barroux.org)
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


class donation_tax_receipt_print(orm.TransientModel):
    _name = 'donation.tax.receipt.print'
    _description = 'Print Donation Tax Receipt'

    _columns = {
        'receipt_ids': fields.many2many(
            'donation.tax.receipt', id1='print_wizard_id', id2='receipt_id',
            string='Receipts To Print'),
    }

    def _get_receipts(self, cr, uid, context=None):
        return self.pool['donation.tax.receipt'].search(
            cr, uid, [('print_date', '=', False)], context=context)

    _defaults = {
        'receipt_ids': _get_receipts,
        }

    def print_receipts(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only 1 ID for a wizard'
        receipt_ids = self.read(
            cr, uid, ids[0], ['receipt_ids'], context=context)['receipt_ids']
        if not receipt_ids:
            raise orm.except_orm(
                _('Error:'),
                _('There are no tax receipts to print.'))

        datas = {
            'model': 'donation.tax.receipt',
            'ids': receipt_ids,
        }
        today = fields.date.context_today(self, cr, uid, context=context)
        self.pool['donation.tax.receipt'].write(
            cr, uid, receipt_ids, {'print_date': today}, context=context)
        action = {
            'type': 'ir.actions.report.xml',
            'report_name': 'donation.tax.receipt.webkit',
            'datas': datas,
            'context': context,
        }
        return action
