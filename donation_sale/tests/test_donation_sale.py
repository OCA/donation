# © 2018-Today Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestDonationSale(TransactionCase):
    def setUp(self):
        super(TestDonationSale, self).setUp()
        self.SaleOrder = self.env['sale.order']
        self.SaleOrderLine = self.env['sale.order.line']
        self.AccountAccount = self.env['account.account']
        self.partner_18 = self.env.ref('base.res_partner_18')
        self.product_4 = self.env.ref('product.product_product_4')
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        self.type_revenue = self.env.ref('account.data_account_type_revenue')
        self.dt_receipt = self.env['donation.tax.receipt']
        self.company = self.env.ref('base.main_company')
        self.product_id =\
            self.env.ref('donation_base.product_product_donation')

        self.product_4.tax_receipt_ok = True
        self.sale_order_id = self.SaleOrder.create({
            'partner_id': self.partner_18.id,
            'tax_receipt_option': 'annual',
            'order_line': [(0, 0, {
                'name': 'PC Assamble + 2GB RAM',
                'product_id': self.product_4.id,
                'product_uom_qty': 1,
                'product_uom': self.product_uom_unit.id,
                'price_unit': 750.00,
            })]
        })

    def test_sale_order(self):
        self.sale_order_id._compute_tax_receipt_total()
        self.sale_order_id.donation_sale_change()
        self.sale_order_id.tax_receipt_option_change()
        context = {
            "active_model": 'sale.order',
            "active_ids": [self.sale_order_id.id],
            "active_id": self.sale_order_id.id
        }
        self.sale_order_id.with_context(context).action_confirm()
        advance_product = self.env.ref('sale.advance_product_0')
        advance_product.property_account_income_id =\
            self.AccountAccount.search([
                ('user_type_id', '=', self.type_revenue.id)], limit=1)
        payment = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'fixed',
            'amount': 500,
            'product_id': advance_product.id,
        })
        payment.with_context(context).create_invoices()
        with self.assertRaises(UserError):
            self.sale_order_id.action_invoice_create()

        self.invoice_id = self.sale_order_id.invoice_ids[0]

        self.dt_receipt_rec = self.dt_receipt.create({
            'date': fields.Date.today(),
            'donation_date': fields.Date.today(),
            'print_date': fields.Date.today(),
            'amount': 101,
            'partner_id': self.partner_18.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'type': 'each',
        })
        self.dt_receipt_rec.action_print()
        self.dt_receipt_rec.action_send_tax_receipt()
        self.invoice_id.tax_receipt_id = self.dt_receipt_rec.id

        self.invoice_id.tax_receipt_option = 'each'
        self.invoice_id._compute_tax_receipt_total()
        self.invoice_id.donation_sale_change()
        self.invoice_id.action_invoice_open()
        self.invoice_id.pay_and_reconcile(
            self.env['account.journal'].search([('type', '=', 'bank')], limit=1
                                               ), 10050.0)

        self.invoice_id.action_invoice_paid()
        self.invoice_id._generate_each_tax_receipts()
        self.invoice_id.tax_receipt_option_change()

        with self.assertRaises(UserError):
            self.invoice_id.action_cancel()

    def test_tax_receipt_annual_create(self):
        self.annual_create = self.env['tax.receipt.annual.create']
        self.annual_create_id = self.annual_create.create({
            'start_date': time.strftime('2017-%m-%d'),
            'end_date': time.strftime('2017-%m-%d'),
        })
        with self.assertRaises(UserError):
            self.annual_create_id.generate_annual_receipts()
