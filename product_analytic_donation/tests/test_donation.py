# Copyright 2017-2021 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestDonationLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "test product 01",
            }
        )
        cls.plan = cls.env["account.analytic.plan"].create({"name": "AxisDonationTest"})
        cls.analytic_account1 = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account1", "plan_id": cls.plan.id}
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account2", "plan_id": cls.plan.id}
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product 02",
                "income_analytic_account_id": cls.analytic_account1.id,
                "expense_analytic_account_id": cls.analytic_account2.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "code": "TEST", "type": "bank"}
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "test_payment_mode",
                "donation": True,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        cls.donor1 = cls.env["res.partner"].create({"name": "Donor Test"})
        cls.donation = cls.env["donation.donation"].create(
            {
                "partner_id": cls.donor1.id,
                "donation_date": "2021-07-21",
                "payment_mode_id": cls.payment_mode.id,
                "line_ids": [
                    Command.create(
                        {
                            "quantity": 1,
                            "unit_price": 50,
                            "product_id": cls.product1.id,
                        },
                    )
                ],
            }
        )
        cls.donation_line = cls.donation.line_ids[0]

    def test_create(self):
        donation2 = (
            self.env["donation.donation"]
            .with_context(default_donation=True)
            .create(
                {
                    "partner_id": self.donor1.id,
                    "donation_date": "2025-05-20",
                    "payment_mode_id": self.payment_mode.id,
                    "line_ids": [
                        Command.create(
                            {
                                "quantity": 1,
                                "unit_price": 50,
                                "product_id": self.product2.id,
                            },
                        )
                    ],
                }
            )
        )
        donation_line2 = donation2.line_ids[0]
        self.assertEqual(
            donation_line2.analytic_distribution.get(
                str(self.product2.income_analytic_account_id.id)
            ),
            100,
        )
