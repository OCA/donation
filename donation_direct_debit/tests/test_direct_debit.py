# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDirectDebit(TransactionCase):
    def test_direct_debit(self):
        donation = self.env.ref("donation_direct_debit.donation6")
        account = self.env["account.account"].create(
            {
                "company_id": donation.company_id.id,
                "code": "TESTDD1",
                "name": "Test donation by direct debit",
                "account_type": "asset_receivable",
            }
        )
        donation.company_id.write({"donation_debit_order_account_id": account.id})
        dd_payment_mode = self.env.ref(
            "account_banking_sepa_direct_debit.payment_mode_inbound_sepa_dd1"
        )
        bank_journal = self.env["account.journal"].create(
            {
                "type": "bank",
                "name": "Bank account test",
            }
        )
        dd_payment_mode.write(
            {
                "donation": True,
                "bank_account_link": "fixed",
                "fixed_journal_id": bank_journal.id,
            }
        )
        donation.validate()
        self.assertEqual(donation.state, "done")
        self.assertTrue(donation.move_id)
        self.assertEqual(donation.mandate_id, donation.move_id.mandate_id)
        self.assertEqual(donation.payment_mode_id, donation.move_id.payment_mode_id)
        paylines = self.env["account.payment.line"].search(
            [
                ("communication", "=", donation.payment_ref),
                ("partner_id", "=", donation.commercial_partner_id.id),
            ]
        )
        self.assertEqual(len(paylines), 1)
        payline = paylines[0]
        self.assertFalse(
            donation.currency_id.compare_amounts(
                payline.amount_currency, donation.check_total
            )
        )
        self.assertEqual(payline.currency_id, donation.currency_id)
        self.assertTrue(payline.move_line_id in donation.move_id.line_ids)
        self.assertEqual(payline.partner_bank_id, donation.mandate_id.partner_bank_id)
        self.assertEqual(payline.mandate_id, donation.mandate_id)
        self.assertEqual(payline.order_id.state, "draft")
