# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestDonationRecurring(TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super().setUp()
        self.bank_journal = self.env["account.journal"].create(
            {
                "type": "bank",
                "name": "test bank journal",
            }
        )
        self.payment_mode = self.env["account.payment.mode"].create(
            {
                "name": "test_payment_mode",
                "donation": True,
                "bank_account_link": "fixed",
                "fixed_journal_id": self.bank_journal.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        self.product = self.env.ref("donation_base.product_product_donation")
        self.ddo = self.env["donation.donation"]
        self.don_rec1 = self.ddo.create(
            {
                "check_total": 30,
                "partner_id": self.env.ref("donation_recurring.donor_rec1").id,
                "donation_date": time.strftime("%Y-01-01"),
                "payment_mode_id": self.payment_mode.id,
                "tax_receipt_option": "annual",
                "recurring_template": "active",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "unit_price": 30,
                        },
                    )
                ],
            }
        )
        self.don_rec2 = self.ddo.create(
            {
                "check_total": 25,
                "partner_id": self.env.ref("donation_recurring.donor_rec2").id,
                "donation_date": time.strftime("%Y-01-01"),
                "payment_mode_id": self.payment_mode.id,
                "tax_receipt_option": "annual",
                "recurring_template": "active",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "unit_price": 25,
                        },
                    )
                ],
            }
        )
        self.don_rec3 = self.ddo.create(
            {
                "check_total": 35,
                "partner_id": self.env.ref("donation_recurring.donor_rec3").id,
                "donation_date": time.strftime("%Y-01-01"),
                "payment_mode_id": self.payment_mode.id,
                "tax_receipt_option": "annual",
                "recurring_template": "suspended",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "unit_price": 35,
                        },
                    )
                ],
            }
        )

    def test_donation_recurring(self):
        wizard = self.env["donation.recurring.generate"].create(
            {"payment_ref": "Don Abbaye Sainte Madeleine"}
        )
        action = wizard.generate()
        active_don_recs = self.don_rec1 + self.don_rec2
        regular_donation_ids = action["domain"][0][2]
        for don_rec in active_don_recs:
            self.assertTrue(don_rec.recurring_donation_ids)
            don = don_rec.recurring_donation_ids[0]
            self.assertEqual(don.state, "draft")
            self.assertEqual(don.payment_ref, "Don Abbaye Sainte Madeleine")
            self.assertEqual(don.campaign_id, don_rec.campaign_id)
        self.assertFalse(self.don_rec3.recurring_donation_ids)
        # Validate the donations generated from the recurring donations templates
        validate_wizard = (
            self.env["donation.validate"]
            .with_context(
                active_ids=regular_donation_ids, active_model="donation.donation"
            )
            .create({})
        )
        validate_wizard.run()
        for don_rec in active_don_recs:
            self.assertTrue(don_rec.recurring_donation_ids)
            don = don_rec.recurring_donation_ids[0]
            self.assertEqual(don.state, "done")
        # Check that recurring donation templates cannot be validated
        donation_template_ids = (self.don_rec1 + self.don_rec2 + self.don_rec3).ids
        validate_wizard_donation_template = (
            self.env["donation.validate"]
            .with_context(
                active_ids=donation_template_ids, active_model="donation.donation"
            )
            .create({})
        )
        with self.assertRaises(ValidationError):
            validate_wizard_donation_template.run()
        self.don_rec1.recurring_template_change()
