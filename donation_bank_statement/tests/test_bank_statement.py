# © 2019 Thore Baden <thorebaden@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestCompany(TransactionCase):

    def setUp(self):
        super(TestCompany, self).setUp()
        self.bank_statement = self.env.ref(
            'account.demo_bank_statement_1'
        )

    def test_create_donations_journal_false(self):
        bank_statement = self.bank_statement
        bank_statement.company_id.donation_credit_transfer_journal_id = False
        self.assertFalse(bank_statement.create_donations())

    def test_create_donations_no_journal(self):
        bank_statement = self.bank_statement
        journal = bank_statement.company_id.donation_credit_transfer_journal_id
        journal.default_debit_account_id = False
        with self.assertRaises(exceptions.UserError):
            self.assertFalse(bank_statement.create_donations())
