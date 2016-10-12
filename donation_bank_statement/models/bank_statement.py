# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.tools import float_compare
from openerp.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def _find_donation_product(self, stline, company):
        '''This method is designed to be inherited'''
        if not company.donation_credit_transfer_product_id:
            raise UserError(_(
                "Missing Product for Donations via Credit Transfer "
                "on company %s") % company.name)
        return company.donation_credit_transfer_product_id

    @api.model
    def _prepare_donation_vals(self, stline, move_line):
        statement = stline.statement_id
        company = statement.company_id
        product = self._find_donation_product(stline, company)
        amount = move_line.credit
        line_vals = {
            'product_id': product.id,
            'quantity': 1,
            'unit_price': amount,
            }
        vals = {
            'company_id': company.id,
            'partner_id': stline.partner_id.id,
            'journal_id': company.donation_credit_transfer_journal_id.id,
            'currency_id': company.currency_id.id,
            'payment_ref': _('Credit Transfer %s') % stline.ref,
            'check_total': amount,
            'donation_date': stline.date,
            'campaign_id': False,
            'bank_statement_line_id': stline.id,
            'line_ids': [(0, 0, line_vals)],
            }
        return vals

    @api.multi
    def create_donations(self):
        self.ensure_one()
        ddo = self.env['donation.donation']
        precision = self.env['decimal.precision'].precision_get('Account')
        assert self.state == 'confirm',\
            'Statement must be in confirm state'
        if not self.company_id.donation_credit_transfer_journal_id:
            raise UserError(
                _("You must configure the Journal for Donations via "
                    "Credit Transfer for the company %s")
                % self.company_id.name)
        journal = self.company_id.donation_credit_transfer_journal_id
        if not journal.default_debit_account_id:
            raise UserError(
                _("Missing Default Debit Account on the Journal '%s'.")
                % journal.name)
        donation_ids = []
        transit_account = journal.default_debit_account_id
        for stline in self.line_ids:
            if (
                    float_compare(
                        stline.amount, 0, precision_digits=precision) == 1 and
                    not stline.donation_ids):
                for amline in stline.journal_entry_ids:
                    for mline in amline.line_ids:
                        if (
                                float_compare(
                                    mline.credit, 0,
                                    precision_digits=precision) == 1 and
                                mline.account_id == transit_account and
                                not mline.reconciled):
                            if not stline.partner_id:
                                raise UserError(
                                    _("Missing partner on bank statement line "
                                        "'%s' dated %s with amount %s.")
                                    % (stline.name, stline.date,
                                        stline.amount))
                            vals = self._prepare_donation_vals(stline, mline)
                            donation = ddo.create(vals)
                            donation.partner_id_change()
                            donation.line_ids.product_id_change()
                            donation_ids.append(donation.id)

        if not donation_ids:
            raise UserError(
                _('No new donation to generate for this bank statement.'))
        action = self.env['ir.actions.act_window'].for_xml_id(
            'donation', 'donation_action')
        action.update({
            'view_mode': 'tree,form,graph',
            'domain': [('id', 'in', donation_ids)],
            'target': 'current',
            })
        return action


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    donation_ids = fields.One2many(
        'donation.donation', 'bank_statement_line_id', string='Donations')
