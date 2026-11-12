# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestDonationPortal(HttpCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Donation Product",
                "donation_type": "donation",
                "type": "service",
                "list_price": 10.0,
                "taxes_id": False,
            }
        )
        cls.product_inkind = cls.env["product.template"].create(
            {
                "name": "Test In-Kind Product",
                "donation_type": "donation_in_kind",
                "type": "consu",
                "list_price": 5.0,
                "taxes_id": False,
            }
        )
        cls.partner1 = cls.env["res.partner"].create({"name": "Donor 1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Donor 2"})
        cls.user1 = cls._create_portal_user("portal_donor_1", cls.partner1)
        cls.user2 = cls._create_portal_user("portal_donor_2", cls.partner2)
        cls.donation1 = cls._create_donation(
            cls.partner1,
            "done",
            [
                (cls.product, 1, 50.0),
                (cls.product_inkind, 2, 10.0),
            ],
        )
        cls.donation_draft = cls._create_donation(
            cls.partner1,
            "draft",
            [(cls.product, 1, 25.0)],
        )
        cls.donation2 = cls._create_donation(
            cls.partner2,
            "done",
            [(cls.product, 1, 75.0)],
        )

    @classmethod
    def _create_portal_user(cls, login, partner):
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "password": login,
                    "email": f"{login}@example.com",
                    "partner_id": partner.id,
                    "groups_id": [Command.set([cls.env.ref("base.group_portal").id])],
                }
            )
        )

    @classmethod
    def _create_donation(cls, partner, state, lines):
        return cls.env["donation.donation"].create(
            {
                "partner_id": partner.id,
                "donation_date": date(2026, 1, 15),
                "state": state,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": quantity,
                            "unit_price": unit_price,
                        }
                    )
                    for product, quantity, unit_price in lines
                ],
            }
        )

    def test_portal_user_sees_only_own_validated_lines(self):
        lines = (
            self.env["donation.line"]
            .with_user(self.user1)
            .search([("donation_id.state", "=", "done")])
        )
        self.assertEqual(lines, self.donation1.line_ids)

    def test_other_portal_user_does_not_see_them(self):
        lines = (
            self.env["donation.line"]
            .with_user(self.user2)
            .search([("donation_id.state", "=", "done")])
        )
        self.assertEqual(lines, self.donation2.line_ids)
        self.assertNotIn(self.donation1.line_ids, lines)

    def test_portal_user_sees_no_draft_line(self):
        lines = self.env["donation.line"].with_user(self.user1).search([])
        self.assertNotIn(self.donation_draft.line_ids, lines)

    def test_my_donations_route_200(self):
        self.authenticate(self.user1.login, self.user1.login)
        response = self.url_open("/my/donations")
        self.assertEqual(response.status_code, 200)

    def test_my_donations_pagination_route_200(self):
        self.authenticate(self.user1.login, self.user1.login)
        response = self.url_open("/my/donations/page/1")
        self.assertEqual(response.status_code, 200)
