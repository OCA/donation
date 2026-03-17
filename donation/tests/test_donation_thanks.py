# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo import Command
from odoo.tests.common import TransactionCase


class TestDonationThanks(TransactionCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.bank_journal = cls.env["account.journal"].create(
            {
                "type": "bank",
                "name": "test bank journal thanks",
                "company_id": cls.company.id,
            }
        )
        cls.payment_account = cls.env["account.account"].create(
            {
                "name": "Donation Payment account thanks",
                "code": "TESTDONTHANKS",
                "company_ids": [Command.set([cls.company.id])],
                "account_type": "asset_current",
                "reconcile": True,
            }
        )
        cls.payment_method_line = cls.env["account.payment.method.line"].create(
            {
                "name": "test_payment_method_line_thanks",
                "company_id": cls.company.id,
                "payment_account_id": cls.payment_account.id,
                "donation": True,
                "journal_id": cls.bank_journal.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        cls.product = cls.env.ref("donation_base.product_product_donation")
        today = time.strftime("%Y-%m-%d")
        cls.ddo = cls.env["donation.donation"]

        # Create three donations and validate them (thanks letter only
        # makes sense for confirmed donations).
        donation_vals = {
            "company_id": cls.company.id,
            "donation_date": today,
            "payment_method_line_id": cls.payment_method_line.id,
            "tax_receipt_option": "none",
        }
        cls.donor1 = cls.env["res.partner"].create({"name": "Thanks donor 1"})
        cls.donor2 = cls.env["res.partner"].create({"name": "Thanks donor 2"})
        cls.donor3 = cls.env["res.partner"].create({"name": "Thanks donor 3"})

        cls.don1 = cls.ddo.create(
            {
                **donation_vals,
                "check_total": 100,
                "partner_id": cls.donor1.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "unit_price": 100,
                        }
                    )
                ],
            }
        )
        cls.don2 = cls.ddo.create(
            {
                **donation_vals,
                "check_total": 200,
                "partner_id": cls.donor2.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "unit_price": 200,
                        }
                    )
                ],
            }
        )
        cls.don3 = cls.ddo.create(
            {
                **donation_vals,
                "check_total": 300,
                "partner_id": cls.donor3.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "unit_price": 300,
                        }
                    )
                ],
            }
        )
        (cls.don1 | cls.don2 | cls.don3).validate()

    def test_thanks_printed_default(self):
        """thanks_printed defaults to False on new donations."""
        self.assertFalse(self.don1.thanks_printed)
        self.assertFalse(self.don2.thanks_printed)
        self.assertFalse(self.don3.thanks_printed)

    def test_print_thanks_single(self):
        """print_thanks() on a single record sets thanks_printed and returns
        a report action."""
        self.assertFalse(self.don1.thanks_printed)
        action = self.don1.print_thanks()
        self.assertTrue(self.don1.thanks_printed)
        # The action must be a dict pointing at the thanks report.
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.report")
        self.assertEqual(action.get("report_name"), "donation.report_donation_thanks")

    def test_print_thanks_multi(self):
        """print_thanks() on a multi-record recordset sets thanks_printed
        on every record."""
        donations = self.don1 | self.don2 | self.don3
        for don in donations:
            self.assertFalse(don.thanks_printed)
        action = donations.print_thanks()
        for don in donations:
            self.assertTrue(don.thanks_printed)
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.report")

    def test_print_thanks_idempotent(self):
        """Calling print_thanks() twice does not raise and the flag
        stays True."""
        self.don1.print_thanks()
        self.assertTrue(self.don1.thanks_printed)
        # Second call should not fail.
        action = self.don1.print_thanks()
        self.assertTrue(self.don1.thanks_printed)
        self.assertIsInstance(action, dict)

    def test_thanks_printed_not_copied(self):
        """thanks_printed is not carried over when duplicating a donation."""
        self.don1.print_thanks()
        self.assertTrue(self.don1.thanks_printed)
        don_copy = self.don1.copy()
        self.assertFalse(don_copy.thanks_printed)

    def test_thanks_template_not_copied(self):
        """thanks_template_id is not carried over when duplicating."""
        template = self.env["donation.thanks.template"].create(
            {"name": "Test template"}
        )
        self.don1.thanks_template_id = template
        don_copy = self.don1.copy()
        self.assertFalse(don_copy.thanks_template_id)

    def test_server_action_calls_print_thanks(self):
        """The ir.actions.server bound to donation.donation invokes
        print_thanks() which sets thanks_printed on all selected records."""
        donations = self.don1 | self.don2
        for don in donations:
            self.assertFalse(don.thanks_printed)
        server_action = self.env.ref("donation.action_print_thanks")
        server_action.with_context(
            active_model="donation.donation",
            active_ids=donations.ids,
        ).run()
        for don in donations:
            self.assertTrue(don.thanks_printed)

    def test_report_not_bound_to_model(self):
        """The ir.actions.report should not be directly bound to the model
        (the server action handles the binding instead)."""
        report = self.env.ref("donation.report_thanks")
        self.assertFalse(report.binding_model_id)
