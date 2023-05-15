# -*- coding: utf-8 -*-
# © 2016-2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestDirectDebit(TransactionCase):

    def test_direct_debit(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        donation = self.env.ref('donation_direct_debit.donation6')
        # It is important to have
        # journal_id.default_debit_account_id.reconcile = True
        # to get a value on move_line.amount_residual
        # By pass a constraint because we can't change to reconcile=True
        # when there are already some moves in the account
        dd_account = self.env['account.account'].create({
            'code': '511DDTEST',
            'name': 'Donations via direct debit',
            'reconcile': True,
            'user_type_id':
            self.env.ref('account.data_account_type_current_assets').id,
            })
        dd_journal = self.env['account.journal'].create({
            'name': 'Donations via Direct debit',
            'code': 'DONDD',
            'type': 'bank',
            'default_credit_account_id': dd_account.id,
            'default_debit_account_id': dd_account.id,
            })
        donation.journal_id = dd_journal.id
        donation.validate()
        self.assertEquals(donation.state, 'done')
        self.assertTrue(donation.move_id)
        mline = False
        for line in donation.move_id.line_ids:
            if line.account_id == donation.journal_id.default_debit_account_id:
                self.assertEquals(donation.mandate_id, line.mandate_id)
                self.assertEquals(
                    donation.payment_mode_id, line.payment_mode_id)
                mline = line
                break
        paylines = self.env['account.payment.line'].search(
            [('move_line_id', '=', mline.id)])
        self.assertEquals(len(paylines), 1)
        payline = paylines[0]
        self.assertEquals(payline.partner_id, donation.commercial_partner_id)
        self.assertFalse(float_compare(
            payline.amount_currency, 150, precision_digits=precision))
        self.assertEquals(payline.currency_id, donation.currency_id)
        self.assertEquals(payline.communication, 'Don prelev SEPA')
        self.assertEquals(
            payline.partner_bank_id, donation.mandate_id.partner_bank_id)
        self.assertEquals(payline.mandate_id, donation.mandate_id)
        self.assertEquals(payline.order_id.state, 'draft')
