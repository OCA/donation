# © 2019 Thore Baden <thorebaden@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from odoo.tests.common import TransactionCase


class TestCompany(TransactionCase):

    def setUp(self):
        super(TestCompany, self).setUp()
        BankStatement = self.env['account.bank.statement']
        BankStatementLine = self.env['account.bank.statement.line']
        Donation = self.env['donation.donation']
        DonationLine = self.env['donation.line']
        self.company = self.env.ref('base.main_company')
        self.journal = self.company.donation_credit_transfer_journal_id
        self.product = self.env.ref('donation_base.product_product_donation')
        self.product.lst_price = 50
        self.bank_statement_2 = BankStatement.create({
            'journal_id': self.journal.id,
            'date': time.strftime('%Y')+'-01-01',
            'name': "BNK/2019/001",
            'state': 'open',
            'balance_end_real': '6278.00',
            'balance_start': 5103.0
        })
        self.bank_statement_line_1 = BankStatementLine.create({
            'ref': '',
            'statement_id': self.bank_statement_2.id,
            'sequence': 1,
            'name': "SAJ/2014/002 and SAJ/2014/003",
            'journal_id': self.journal.id,
            'amount': 1175.0,
            'date': time.strftime('%Y')+'-01-01',
            'partner_id': self.ref('base.res_partner_2'),
        })
        self.donation = Donation.create({
            'partner_id': self.ref('base.res_partner_2'),
            'donation_date': time.strftime('%Y')+'-01-01',
            'bank_statement_line_id': self.bank_statement_line_1.id,
            'journal_id': self.journal.id,
        })
        self.donation_line = DonationLine.create({
            'product_id': self.product.id,
            'quantity': 1,
            'donation_id': self.donation.id,
            'unit_price': 50,
        })

    def test_donation_validate(self):
        journal = self.journal
        self.assertEqual(journal.id, 8)
        journal.default_debit_account_id.reconcile = True
        self.donation.validate()
