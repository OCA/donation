# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestDonationLine(TransactionCase):

    def setUp(self):
        super(TestDonationLine, self).setUp()
        self.product1 = self.env['product.product'].create({
            'name': 'test product 01',
            })
        self.analytic_account1 = self.env['account.analytic.account'].create({
            'name': 'test analytic_account1'})
        self.analytic_account2 = self.env['account.analytic.account'].create({
            'name': 'test analytic_account2'})
        self.product2 = self.env['product.product'].create({
            'name': 'test product 02',
            'income_analytic_account_id': self.analytic_account1.id,
            'expense_analytic_account_id': self.analytic_account2.id,
            })
        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'code': 'TEST',
            'type': 'bank'})
        self.account_type = self.env['account.account.type'].create({
            'name': 'Test account type',
            'type': 'other'})
        self.account = self.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': self.account_type.id})
        self.donation = self.env['donation.donation'].create({
            'partner_id': self.env.ref('donation_base.donor1').id,
            'donation_date': '2017-07-21',
            'journal_id': self.journal.id,
            'line_ids': [
                (0, 0, {
                    'quantity': 1,
                    'unit_price': 50,
                    'product_id': self.product1.id,
                })
            ]
        })
        self.donation_line = self.donation.line_ids[0]

    def test_onchange_product_id(self):
        self.donation_line.product_id = self.product2.id
        self.donation_line.product_id_change()
        self.assertEqual(
            self.donation_line.analytic_account_id.id,
            self.product2.income_analytic_account_id.id)

    def test_create(self):
        donation2 = self.env['donation.donation'].create({
            'partner_id': self.env.ref('donation_base.donor1').id,
            'donation_date': '2017-07-20',
            'journal_id': self.journal.id,
            'line_ids': [
                (0, 0, {
                    'quantity': 1,
                    'unit_price': 50,
                    'product_id': self.product2.id,
                })
            ]
        })
        donation_line2 = donation2.line_ids[0]
        self.assertEqual(donation_line2.analytic_account_id.id,
                         self.product2.income_analytic_account_id.id)
