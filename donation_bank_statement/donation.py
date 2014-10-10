# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Bank Statement module for OpenERP
#    Copyright (C) 2014 Artisanat Monastique de Provence
#                       (http://www.barroux.org)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
import logging

logger = logging.getLogger(__name__)


class donation_donation(orm.Model):
    _inherit = 'donation.donation'

    _columns = {
        'bank_statement_line_id': fields.many2one(
            'account.bank.statement.line',
            'Source Bank Statement Line'),
        }

    def validate(self, cr, uid, ids, context=None):
        res = super(donation_donation, self).validate(
            cr, uid, ids, context=context)
        donation = self.browse(cr, uid, ids[0], context=context)
        if donation.bank_statement_line_id:
            donation_mline_id = False
            statement_mline_id = False
            transit_account = donation.journal_id.default_debit_account_id
            for donation_mline in donation.move_id.line_id:
                if (
                        donation_mline.account_id == transit_account
                        and not donation_mline.reconcile_id):
                    donation_mline_id = donation_mline.id
                    logger.info(
                        'Found donation move line to reconcile ID=%d'
                        % donation_mline_id)
                    break
            for statement_mline in\
                    donation.bank_statement_line_id.journal_entry_id.line_id:
                if (
                        statement_mline.account_id == transit_account
                        and not statement_mline.reconcile_id):
                    statement_mline_id = statement_mline.id
                    logger.info(
                        'Found bank statement move line to reconcile ID=%d'
                        % statement_mline_id)
                    break
            if donation_mline_id and statement_mline_id:
                reconcile_id = self.pool['account.move.line'].reconcile(
                    cr, uid, [donation_mline_id, statement_mline_id],
                    context=context)
                logger.info(
                    'Successfull reconcilation between donation and '
                    'bank statement. Reconcile mark ID=%d' % reconcile_id)
        return res
