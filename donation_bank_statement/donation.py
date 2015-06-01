# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Bank Statement module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
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

from openerp import models, fields, api
import logging

logger = logging.getLogger(__name__)


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    bank_statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        string='Source Bank Statement Line', ondelete='restrict')

    @api.one
    def validate(self):
        res = super(DonationDonation, self).validate()
        if self.bank_statement_line_id:
            donation_mline_rec = False
            statement_mline_rec = False
            transit_account = self.journal_id.default_debit_account_id
            for donation_mline in self.move_id.line_id:
                if (
                        donation_mline.account_id == transit_account and
                        not donation_mline.reconcile_id):
                    donation_mline_rec = donation_mline
                    logger.info(
                        'Found donation move line to reconcile ID=%d'
                        % donation_mline_rec.id)
                    break
            for statement_mline in\
                    self.bank_statement_line_id.journal_entry_id.line_id:
                if (
                        statement_mline.account_id == transit_account and
                        not statement_mline.reconcile_id):
                    statement_mline_rec = statement_mline
                    logger.info(
                        'Found bank statement move line to reconcile ID=%d'
                        % statement_mline_rec.id)
                    break
            if donation_mline_rec and statement_mline_rec:
                mlines_to_reconcile = donation_mline_rec + statement_mline_rec
                reconcile_id = mlines_to_reconcile.reconcile()
                logger.info(
                    'Successfull reconcilation between donation and '
                    'bank statement. Reconcile mark ID=%d' % reconcile_id)
        return res
