# Copyright 2018-Today Serpent Consulting Services Pvt. Ltd.
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time
from datetime import timedelta

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestDonationSale(TransactionCase):
    def setUp(self):
        super().setUp()
        self.SaleOrder = self.env["sale.order"]
        self.partner_18 = self.env.ref("base.res_partner_18")
        self.company = self.env.ref("base.main_company")
        self.product = self.env.ref("donation_base.product_product_donation")

        self.sale_order = self.SaleOrder.create(
            {
                "partner_id": self.partner_18.id,
                "tax_receipt_option": "each",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Donation",
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 750.00,
                        },
                    )
                ],
            }
        )

    def test_sale_order(self):
        self.sale_order.donation_sale_change()
        self.sale_order.tax_receipt_option_change()
        context = {
            "active_model": "sale.order",
            "active_ids": [self.sale_order.id],
            "active_id": self.sale_order.id,
        }
        self.sale_order.with_context(context).action_confirm()
        for line in self.sale_order.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        payment = self.env["sale.advance.payment.inv"].create({})
        payment.with_context(context).create_invoices()

        self.invoice = self.sale_order.invoice_ids[0]
        self.invoice.action_post()
        self.assertEqual(self.invoice.state, "posted")
        self.assertEqual(self.invoice.tax_receipt_option, "each")
        self.assertFalse(self.invoice.tax_receipt_id)

        bank_journal = self.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", self.invoice.company_id.id)],
            limit=1,
        )
        payment_date = self.invoice.invoice_date + timedelta(days=5)
        wiz = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_id=self.invoice.id,
                active_ids=[self.invoice.id],
            )
            .create(
                {
                    "journal_id": bank_journal.id,
                    "payment_date": payment_date,
                }
            )
        )
        wiz.action_create_payments()
        self.assertEqual(self.invoice.payment_state, "paid")

        self.invoice._generate_each_tax_receipts()
        self.tax_receipt = self.invoice.tax_receipt_id
        self.assertTrue(self.tax_receipt)
        self.assertEqual(self.tax_receipt.type, "each")
        self.assertEqual(
            self.tax_receipt.partner_id, self.invoice.commercial_partner_id
        )
        self.assertEqual(self.tax_receipt.date, payment_date)

        with self.assertRaises(UserError):
            self.invoice.button_cancel()
        self.tax_receipt.action_print()
        self.tax_receipt.action_send_tax_receipt()

    def test_tax_receipt_annual_create(self):
        self.annual_create = self.env["tax.receipt.annual.create"]
        self.annual_create_id = self.annual_create.create(
            {
                "start_date": time.strftime("2017-%m-%d"),
                "end_date": time.strftime("2017-%m-%d"),
            }
        )
        with self.assertRaises(UserError):
            self.annual_create_id.generate_annual_receipts()
