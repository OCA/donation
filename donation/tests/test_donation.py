# Copyright 2015-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestDonation(TransactionCase):
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
                "name": "test bank journal",
                "company_id": cls.company.id,
            }
        )
        cls.payment_account = cls.env["account.account"].create(
            {
                "name": "Donation Payment account",
                "code": "TESTDONATION",
                "company_ids": [Command.set([cls.company.id])],
                "account_type": "asset_current",
                "reconcile": True,
            }
        )
        cls.payment_method_line = cls.env["account.payment.method.line"].create(
            {
                "name": "test_payment_method_line",
                "company_id": cls.company.id,
                "payment_account_id": cls.payment_account.id,
                "donation": True,
                "journal_id": cls.bank_journal.id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        today = time.strftime("%Y-%m-%d")
        cls.product = cls.env.ref("donation_base.product_product_donation")
        cls.inkind_product = cls.env.ref(
            "donation_base.product_product_inkind_donation"
        )
        cls.ddo = cls.env["donation.donation"]
        cls.donor1 = cls.env["res.partner"].create({"name": "Test donor1"})
        cls.donor2 = cls.env["res.partner"].create({"name": "Test donor2"})
        cls.donor3 = cls.env["res.partner"].create({"name": "Test donor3"})

        cls.don1 = cls.ddo.create(
            {
                "company_id": cls.company.id,
                "check_total": 100,
                "partner_id": cls.donor1.id,
                "donation_date": today,
                "payment_method_line_id": cls.payment_method_line.id,
                "tax_receipt_option": "each",
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
                "company_id": cls.company.id,
                "check_total": 120,
                "partner_id": cls.donor2.id,
                "donation_date": today,
                "payment_method_line_id": cls.payment_method_line.id,
                "tax_receipt_option": "annual",
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "unit_price": 120,
                        }
                    )
                ],
            }
        )
        cls.don3 = cls.ddo.create(
            {
                "company_id": cls.company.id,
                "check_total": 150,
                "partner_id": cls.donor3.id,
                "donation_date": today,
                "payment_method_line_id": cls.payment_method_line.id,
                "tax_receipt_option": "none",
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "unit_price": 150,
                        }
                    )
                ],
            }
        )
        cls.don4 = cls.ddo.create(
            {
                "company_id": cls.company.id,
                "check_total": 1000,
                "partner_id": cls.donor1.id,
                "donation_date": today,
                "payment_method_line_id": cls.payment_method_line.id,
                "tax_receipt_option": "each",
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.inkind_product.id,
                            "quantity": 1,
                            "unit_price": 1000,
                        }
                    )
                ],
            }
        )
        cls.don5 = cls.ddo.create(
            {
                "company_id": cls.company.id,
                "check_total": 1200,
                "partner_id": cls.donor1.id,
                "donation_date": today,
                "payment_method_line_id": cls.payment_method_line.id,
                "tax_receipt_option": "each",
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.inkind_product.id,
                            "quantity": 1,
                            "unit_price": 800,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "unit_price": 400,
                        }
                    ),
                ],
            }
        )

    def test_donation_1(self):
        donations = [self.don1, self.don2, self.don3, self.don4, self.don5]
        for donation in donations:
            self.assertEqual(donation.state, "draft")
            donation.validate()
            self.assertEqual(donation.state, "done")
            if donation == self.don4:  # full in-kind donation
                self.assertFalse(donation.move_id)
            else:
                self.assertEqual(donation.move_id.state, "posted")
                self.assertEqual(donation.payment_ref, donation.move_id.ref)
                self.assertEqual(
                    donation.payment_method_line_id.journal_id,
                    donation.move_id.journal_id,
                )
                self.assertEqual(donation.donation_date, donation.move_id.date)
            if donation.tax_receipt_option == "each" and donation.tax_receipt_total:
                self.assertTrue(donation.tax_receipt_id)
                tax_receipt = donation.tax_receipt_id
                self.assertEqual(tax_receipt.type, "each")
                self.assertEqual(donation.commercial_partner_id, tax_receipt.partner_id)
                self.assertEqual(donation.donation_date, tax_receipt.donation_date)
                self.assertEqual(donation.tax_receipt_total, tax_receipt.amount)

    def test_donation_2(self):
        self.donation_id = self.ddo.create(
            {
                "check_total": 1000,
                "partner_id": self.donor1.id,
                "donation_date": time.strftime("%Y-%m-%d"),
                "payment_method_line_id": self.payment_method_line.id,
                "tax_receipt_option": "each",
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.inkind_product.id,
                            "quantity": 1,
                            "unit_price": 1000,
                        }
                    )
                ],
            }
        )
        self.donation_id.save_default_values()
        self.donation_id.tax_receipt_option_change()
        self.donation_id.validate()
        self.donation_id.tax_receipt_id = False
        self.donation_id.done2cancel()
        self.donation_id.cancel2draft()
        self.donation_id.unlink()

    def test_annual_tax_receipt(self):
        self.res_partner = self.env["res.partner"]

        partner_familly = self.res_partner.create(
            {"name": "Famille Joly", "tax_receipt_option": "annual"}
        )
        partner_husband = self.res_partner.create(
            {"parent_id": partner_familly.id, "name": "Xavier Joly"}
        )
        partner_wife = self.res_partner.create(
            {"parent_id": partner_familly.id, "name": "Stéphanie Joly"}
        )

        partner_husband._compute_donation_count()
        dons = self.create_donation_annual_receipt(
            partner_husband, 40, 10, "CHQ FB 93283290"
        )
        dons += self.create_donation_annual_receipt(
            partner_husband, 140, 60, "CHQ FB OPIE02"
        )
        dons += self.create_donation_annual_receipt(
            partner_wife, 20, 5, "CHQ FB AZERTY1242"
        )
        dons.validate()
        last_day_year = time.strftime("%Y-12-31")
        wizard = self.env["tax.receipt.annual.create"].create(
            {"start_date": time.strftime("%Y-01-01"), "end_date": last_day_year}
        )
        action = wizard.generate_annual_receipts()
        tax_receipt_ids = action["domain"][0][2]
        self.assertTrue(tax_receipt_ids)
        dtro = self.env["donation.tax.receipt"]
        tax_receipts = dtro.search(
            [
                ("partner_id", "=", partner_familly.id),
                ("type", "=", "annual"),
                ("id", "in", tax_receipt_ids),
            ]
        )
        self.assertEqual(len(tax_receipts), 1)
        tax_receipt = tax_receipts[0]
        self.assertEqual(tax_receipt.amount, 200)
        self.assertTrue(tax_receipt.number)
        self.assertEqual(tax_receipt.date, fields.Date.from_string(last_day_year))
        self.assertEqual(
            tax_receipt.donation_date, fields.Date.from_string(last_day_year)
        )
        self.assertEqual(tax_receipt.currency_id, dons[0].company_id.currency_id)

    def test_donation_campaign(self):
        self.campaign_id = self.env.ref("donation.quest_origin")

        self.don8 = self.ddo.create(
            {
                "check_total": 1000,
                "partner_id": self.donor1.id,
                "donation_date": time.strftime("%Y-%m-%d"),
                "payment_method_line_id": self.payment_method_line.id,
                "tax_receipt_option": "each",
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.inkind_product.id,
                            "quantity": 1,
                            "unit_price": 1000,
                        }
                    )
                ],
            }
        )

        self.validate = self.env["donation.validate"]
        wizard = self.validate.with_context(
            active_ids=self.don8.ids,
            active_model="donation.donation",
            active_id=self.don8.id,
        ).create({})
        wizard.run()

        self.option_switch = self.env["donation.tax.receipt.option.switch"]
        wizard = self.option_switch.create(
            {"donation_id": self.don8.id, "new_tax_receipt_option": "annual"}
        )
        self.don8.tax_receipt_id = False
        wizard.switch()

    def create_donation_annual_receipt(
        self, partner, amount_tax_receipt, amount_no_tax_receipt, payment_ref
    ):
        donation = self.ddo.create(
            {
                "payment_method_line_id": self.payment_method_line.id,
                "partner_id": partner.id,
                "tax_receipt_option": "annual",
                "donation_date": time.strftime("%Y-01-01"),
                "payment_ref": payment_ref,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "unit_price": amount_tax_receipt,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.env.ref(
                                "donation_base.product_product_donation_notaxreceipt"
                            ).id,
                            "quantity": 1,
                            "unit_price": amount_no_tax_receipt,
                        }
                    ),
                ],
            }
        )
        return donation
