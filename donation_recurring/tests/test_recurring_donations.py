# -*- coding: utf-8 -*-
# Copyright 2016-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import time


class TestDonationRecurring(TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestDonationRecurring, self).setUp()
        self.test_company = self.env['res.company'].create({
            'name': 'TestCharity',
            })
        self.env.user.write({
            'company_id': self.test_company.id,
            'company_ids': [(4, self.test_company.id)],
            })

        generic_coa = self.env.ref(
            'l10n_generic_coa.configurable_chart_template')
        generic_coa.try_loading_for_current_company()
        # Warning: loading coa chart of accounts writes
        # USD as currency of company (even if company was created with
        # EUR as currency. So let's work on USD for the tests

        self.currency = self.test_company.currency_id
        self.bank_journal = self.env['account.journal'].search([
            ('company_id', '=', self.test_company.id),
            ('type', '=', 'bank')], limit=1)
        self.product = self.env.ref(
            'donation_base.product_product_donation')
        self.inkind_product = self.env.ref(
            'donation_base.product_product_inkind_donation')
        self.ddo = self.env['donation.donation']
        self.don_rec1 = self.ddo.create({
            'company_id': self.test_company.id,
            'currency_id': self.currency.id,
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
            'company_id': self.test_company.id,
            'currency_id': self.currency.id,
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
            'company_id': self.test_company.id,
            'currency_id': self.currency.id,
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
            self.assertEquals(don.amount_total, don_rec.amount_total)
            self.assertEquals(
                don.payment_ref,
                'Don Abbaye Sainte Madeleine')
            self.assertEquals(don.campaign_id, don_rec.campaign_id)
        self.assertFalse(self.don_rec3.recurring_donation_ids)
        active_ids = action['domain'][0][2]
        wizard_val = self.env['donation.validate'].with_context(
            active_ids=active_ids, active_model='donation.donation').\
            create({})
        wizard_val.run()
        for don_rec in active_don_recs:
            don = don_rec.recurring_donation_ids[0]
            self.assertEquals(don.state, 'done')
            self.assertEquals(don.move_id.journal_id, don_rec.journal_id)
            self.assertEquals(don.move_id.state, 'posted')
            self.assertEquals(don.move_id.ref, 'Don Abbaye Sainte Madeleine')
