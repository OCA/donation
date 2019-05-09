# © 2019 Thore Baden <thorebaden@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestCompany(TransactionCase):

    def setUp(self):
        super(TestCompany, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.productNoTax = self.ref(
            'donation_base.product_product_donation_notaxreceipt'
        )

    def test_company_donation_bank_statement_check(self):
        self.assertTrue(
            self.company.donation_credit_transfer_product_id.donation
        )
        self.company.company_donation_bank_statement_check()
        self.company.donation_credit_transfer_product_id = self.productNoTax
        self.company.donation_credit_transfer_product_id.donation = False
        with self.assertRaises(exceptions.ValidationError):
            self.company.company_donation_bank_statement_check()
