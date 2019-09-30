# © 2018-Today Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestDonationTaxReceipt(TransactionCase):
    def setUp(self):
        super(TestDonationTaxReceipt, self).setUp()
        self.dt_receipt = self.env['donation.tax.receipt']
        self.partner = self.env.ref('base.res_partner_1')
        self.company = self.env.ref('base.main_company')
        self.product_id =\
            self.env.ref('donation_base.product_product_donation')
        self.dt_receipt_rec = self.dt_receipt.create({
            'date': fields.Date.today(),
            'donation_date': fields.Date.today(),
            'print_date': fields.Date.today(),
            'amount': 101,
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'type': 'each',
        })

    def test_donation(self):
        rec = self.partner._commercial_fields()
        self.assertIn('tax_receipt_option', rec)

        self.partner._compute_tax_receipt_count()
        self.assertTrue(self.partner.tax_receipt_count)

        self.dt_receipt_rec.action_print()
        self.dt_receipt_rec.action_send_tax_receipt()
        self.partner.email = False
        with self.assertRaises(UserError):
            self.dt_receipt_rec.action_send_tax_receipt()

    def test_donation_change(self):
        self.product_id._donation_change()
        self.assertEqual(self.product_id.type, 'service')
        self.product_id._in_kind_donation_change()
        self.assertTrue(self.product_id.donation)

        self.product_id.product_tmpl_id._donation_change()
        self.assertEqual(self.product_id.product_tmpl_id.type, 'service')
        self.product_id.product_tmpl_id._in_kind_donation_change()
        self.assertTrue(self.product_id.product_tmpl_id.donation)

    def test_donation_check_donation(self):
        with self.assertRaises(ValidationError):
            self.product_id.product_tmpl_id.donation = False

    def test_donation_check_kind_donation(self):
        with self.assertRaises(ValidationError):
            self.product_id.product_tmpl_id.in_kind_donation = True
            self.product_id.product_tmpl_id.donation = False


class TestTaxReceiptAnnualCreate(TransactionCase):
    def setUp(self):
        super(TestTaxReceiptAnnualCreate, self).setUp()
        self.dt_receipt = self.env['donation.tax.receipt']
        self.tax_receipt_print = self.env['donation.tax.receipt.print']
        self.partner = self.env.ref('base.res_partner_1')
        self.company = self.env.ref('base.main_company')
        self.dt_receipt_rec = self.dt_receipt.create({
            'date': fields.Date.today(),
            'donation_date': fields.Date.today(),
            'print_date': fields.Date.today(),
            'amount': 101,
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'type': 'each',
        })
        self.tax_receipt_print_rec = self.tax_receipt_print.create({
            'receipt_ids': [(6, 0, [self.dt_receipt_rec.id])],
        })

    def test_wizard_methods(self):
        self.tax_receipt_print_rec.print_receipts()

    def test_tax_receipt_annual_create(self):
        self.annual_create = self.env['tax.receipt.annual.create']
        self.annual_create_id = self.annual_create.create({
            'start_date': time.strftime('2017-%m-%d'),
            'end_date': time.strftime('2017-%m-%d'),
        })
        with self.assertRaises(UserError):
            self.annual_create_id.generate_annual_receipts()
