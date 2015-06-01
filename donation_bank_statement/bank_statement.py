# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Bank Statement module for Odoo
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


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def _find_product_id(self, stline):
        products = self.env['product.product'].search(
            [('donation', '=', True)])
        assert products, 'No donation products'
        return products[0].id

    @api.model
    def _prepare_donation_vals(self, stline, move_line):
        product_id = self._find_product_id(stline)
        statement = stline.statement_id
        company = statement.company_id
        amount = move_line.credit
        line_vals = {
            'product_id': product_id,
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
        assert self.state == 'confirm',\
            'Statement must be in confirm state'
        if not self.company_id.donation_credit_transfer_journal_id:
            raise Warning(
                _("You must configure the Journal for Donations via "
                    "Credit Transfer for the company %s")
                % self.company_id.name)
        journal = self.company_id.donation_credit_transfer_journal_id
        if not journal.default_debit_account_id:
            raise Warning(
                _("Missing Default Debit Account on the Journal '%s'.")
                % journal.name)
        donation_ids = []
        transit_account = journal.default_debit_account_id
        for stline in self.line_ids:
            if stline.amount > 0 and not stline.donation_ids:
                for mline in stline.journal_entry_id.line_id:
                    if (
                            mline.credit > 0 and
                            mline.account_id == transit_account and
                            not mline.reconcile_id):
                        if not stline.partner_id:
                            raise Warning(
                                _("Missing partner on bank statement line "
                                    "'%s' dated %s with amount %s.")
                                % (stline.name, stline.date, stline.amount))
                        vals = self._prepare_donation_vals(stline, mline)
                        donation = self.env['donation.donation'].create(vals)
                        donation.partner_id_change()
                        donation.line_ids.product_id_change()
                        donation_ids.append(donation.id)

        if not donation_ids:
            raise Warning(
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
