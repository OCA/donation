# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Bank Statement module for OpenERP
#    Copyright (C) 2014 Barroux Abbey (www.barroux.org)
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


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def _find_product_id(
            self, cr, uid, stline, context=None):
        product_ids = self.pool['product.product'].search(
            cr, uid, [('donation', '=', True)], context=context)
        assert product_ids, 'No donation products'
        return product_ids[0]

    def _prepare_donation_vals(
            self, cr, uid, stline, move_line, context=None):
        product_id = self._find_product_id(
            cr, uid, stline, context=context)
        statement = stline.statement_id
        company = statement.company_id
        company_id = statement.company_id.id
        amount = move_line.credit
        product_change = self.pool['donation.line'].product_id_change(
            cr, uid, [], product_id, context=context)
        line_vals = product_change['value']
        line_vals.update({
            'product_id': product_id,
            'quantity': 1,
            'unit_price': amount,
            })
        partner_change = self.pool['donation.donation'].partner_id_change(
            cr, uid, [], stline.partner_id.id, company_id,
            context=context)
        if partner_change and partner_change.get('value'):
            vals = partner_change['value']
        else:
            vals = {}
        vals.update({
            'company_id': company_id,
            'partner_id': stline.partner_id.id,
            'journal_id': company.donation_credit_transfer_journal_id.id,
            'currency_id': company.currency_id.id,
            'payment_ref': _('Credit Transfer %s') % stline.ref,
            'check_total': amount,
            'donation_date': stline.date,
            'campaign_id': False,
            'bank_statement_line_id': stline.id,
            'line_ids': [(0, 0, line_vals)],
        })
        return vals

    def create_donations(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only 1 ID allowed here'
        statement = self.browse(cr, uid, ids[0], context=context)
        assert statement.state == 'confirm',\
            'Statement must be in confirm state'
        if not statement.company_id.donation_credit_transfer_journal_id:
            raise orm.except_orm(
                _('Error:'),
                _("You must configure the Journal for Donations via "
                    "Credit Transfer for the company %s")
                % statement.company_id.name)
        journal = statement.company_id.donation_credit_transfer_journal_id
        if not journal.default_debit_account_id:
            raise orm.except_orm(
                _('Error:'),
                _("Missing Default Debit Account on the Journal '%s'.")
                % journal.name)
        donation_ids = []
        transit_account = journal.default_debit_account_id
        for stline in statement.line_ids:
            if stline.amount > 0 and not stline.donation_ids:
                for mline in stline.journal_entry_id.line_id:
                    if (
                            mline.credit > 0
                            and mline.account_id == transit_account
                            and not mline.reconcile_id):
                        vals = self._prepare_donation_vals(
                            cr, uid, stline, mline, context=context)
                        donation_id = self.pool['donation.donation'].create(
                            cr, uid, vals, context=context)
                        donation_ids.append(donation_id)

        if not donation_ids:
            raise orm.except_orm(
                _('Error:'),
                _('No new donation to generate from this bank statement.'))
        action_id = self.pool['ir.model.data'].xmlid_to_res_id(
            cr, uid, 'donation.donation_action', raise_if_not_found=True)
        action = self.pool['ir.actions.act_window'].read(
            cr, uid, action_id, context=context)
        action.update({
            'view_mode': 'tree,form,graph',
            'domain': [('id', 'in', donation_ids)],
            'target': 'current',
            })
        return action


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    _columns = {
        'donation_ids': fields.one2many(
            'donation.donation', 'bank_statement_line_id', 'Donations'),
        }
