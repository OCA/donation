# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    bank_statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        string='Source Bank Statement Line', ondelete='restrict')

    @api.multi
    def validate(self):
        res = super(DonationDonation, self).validate()
        for donation in self:
            if donation.bank_statement_line_id:
                donation_mline_rec = False
                statement_mline_rec = False
                transit_account = donation.journal_id.default_debit_account_id
                if not transit_account.reconcile:
                    raise UserError(_(
                        "The default debit account of the journal '%s' must "
                        "be reconciliable") % donation.journal_id.name)
                for donation_mline in donation.move_id.line_ids:
                    if (
                            donation_mline.account_id == transit_account and
                            not donation_mline.reconciled):
                        donation_mline_rec = donation_mline
                        logger.info(
                            'Found donation move line to reconcile ID=%d'
                            % donation_mline_rec.id)
                        break
                for statement_amline in\
                        donation.bank_statement_line_id.journal_entry_ids:
                    for statement_mline in statement_amline.line_ids:
                        if (
                                statement_mline.account_id ==
                                transit_account and
                                not statement_mline.reconciled):
                            statement_mline_rec = statement_mline
                            logger.info(
                                'Found bank statement move line to reconcile '
                                'ID=%d', statement_mline_rec.id)
                            break
                if donation_mline_rec and statement_mline_rec:
                    mlines_to_reconcile =\
                        donation_mline_rec + statement_mline_rec
                    mlines_to_reconcile.reconcile()
                    logger.info(
                        'Successfull reconcilation between donation and '
                        'bank statement.')
        return res
