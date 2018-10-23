# -*- coding: utf-8 -*-
# Copyright 2016-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo.tests.common import TransactionCase
from odoo import tools
from odoo.modules.module import get_resource_path
from odoo.exceptions import UserError


class TestDonationRecurring(TransactionCase):

    at_install = False
    post_install = True

    def _load(self, module, *args):
        tools.convert_file(
            self.cr, module, get_resource_path(module, *args),
            {}, 'init', False, 'test', self.registry._assertion_report)

    def setUp(self):
        super(TestDonationRecurring, self).setUp()
        self._load('account', 'test', 'account_minimal_test.xml')

        self.bank_journal = self.env.ref('account.bank_journal')
        self.product = self.env.ref(
            'donation_base.product_product_donation')
        self.inkind_product = self.env.ref(
            'donation_base.product_product_inkind_donation')
        self.ddo = self.env['donation.donation']
        self.don_rec1 = self.ddo.create({
            'check_total': 30,
            'partner_id': self.env.ref('donation_recurring.donor_rec1').id,
            'donation_date': time.strftime('%Y-01-01'),
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'annual',
            'recurring_template': 'active',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 30,
                })],
            })
        self.don_rec2 = self.ddo.create({
            'check_total': 25,
            'partner_id': self.env.ref('donation_recurring.donor_rec2').id,
            'donation_date': time.strftime('%Y-01-01'),
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'annual',
            'recurring_template': 'active',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 25,
                })],
            })
        self.don_rec3 = self.ddo.create({
            'check_total': 35,
            'partner_id': self.env.ref('donation_recurring.donor_rec3').id,
            'donation_date': time.strftime('%Y-01-01'),
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'annual',
            'recurring_template': 'suspended',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 35,
                })],
            })

    def test_donation_recurring(self):
        wizard = self.env['donation.recurring.generate'].create(
            {'payment_ref': 'Don Abbaye Sainte Madeleine'})
        action = wizard.generate()
        active_don_recs = self.don_rec1 + self.don_rec2
        for don_rec in active_don_recs:
            self.assertTrue(don_rec.recurring_donation_ids)
            don = don_rec.recurring_donation_ids[0]
            self.assertEquals(don.state, 'draft')
            self.assertEquals(
                don.payment_ref,
                'Don Abbaye Sainte Madeleine')
            self.assertEquals(don.campaign_id, don_rec.campaign_id)
        self.assertFalse(self.don_rec3.recurring_donation_ids)
        active_ids = action['domain'][0][2]
        wizard_val = self.env['donation.validate'].with_context(
            active_ids=active_ids, active_model='donation.donation').\
            create({})
        with self.assertRaises(UserError):
            wizard_val.run()
        self.don_rec1.recurring_template_change()
