# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo.tests.common import TransactionCase
from odoo import fields, tools
from odoo.modules.module import get_resource_path
from odoo.exceptions import ValidationError


class TestDonation(TransactionCase):

    at_install = False
    post_install = True

    def _load(self, module, *args):
        tools.convert_file(
            self.cr, module, get_resource_path(module, *args),
            {}, 'init', False, 'test', self.registry._assertion_report)

    def setUp(self):
        super(TestDonation, self).setUp()
        self._load('account', 'test', 'account_minimal_test.xml')

        self.bank_journal = self.env.ref('account.bank_journal')
        today = time.strftime('%Y-%m-%d'),
        self.product = self.env.ref(
            'donation_base.product_product_donation')
        self.inkind_product = self.env.ref(
            'donation_base.product_product_inkind_donation')
        self.ddo = self.env['donation.donation']
        self.donor1 = self.env.ref('donation_base.donor1')
        self.donor2 = self.env.ref('donation_base.donor2')
        self.donor3 = self.env.ref('donation_base.donor3')

        self.don1 = self.ddo.create({
            'check_total': 100,
            'partner_id': self.donor1.id,
            'donation_date': today,
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'each',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 100,
                })],
            })
        self.don2 = self.ddo.create({
            'check_total': 120,
            'partner_id': self.donor2.id,
            'donation_date': today,
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'annual',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 120,
                })],
            })
        self.don3 = self.ddo.create({
            'check_total': 150,
            'partner_id': self.donor3.id,
            'donation_date': today,
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'none',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 150,
                })],
            })
        self.don4 = self.ddo.create({
            'check_total': 1000,
            'partner_id': self.donor1.id,
            'donation_date': today,
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'each',
            'line_ids': [(0, 0, {
                'product_id': self.inkind_product.id,
                'quantity': 1,
                'unit_price': 1000,
                })],
            })
        self.don5 = self.ddo.create({
            'check_total': 1200,
            'partner_id': self.donor1.id,
            'donation_date': today,
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'each',
            'line_ids': [
                (0, 0, {
                    'product_id': self.inkind_product.id,
                    'quantity': 1,
                    'unit_price': 800,
                    }),
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 1,
                    'unit_price': 400,
                    }),
                ],
            })

    def test_donation_1(self):
        donations = [self.don1, self.don2, self.don3, self.don4, self.don5]
        for donation in donations:
            self.assertEquals(donation.state, 'draft')
            donation.validate()
            self.assertEquals(donation.state, 'done')
            if donation == self.don4:  # full in-kind donation
                self.assertFalse(donation.move_id)
            else:
                self.assertEquals(donation.move_id.state, 'posted')
                self.assertEquals(donation.payment_ref, donation.move_id.ref)
                self.assertEquals(
                    donation.journal_id, donation.move_id.journal_id)
                self.assertEquals(
                    donation.donation_date, donation.move_id.date)
            if (
                    donation.tax_receipt_option == 'each' and
                    donation.tax_receipt_total):
                self.assertTrue(donation.tax_receipt_id)
                tax_receipt = donation.tax_receipt_id
                self.assertEquals(tax_receipt.type, 'each')
                self.assertEquals(
                    donation.commercial_partner_id, tax_receipt.partner_id)
                self.assertEquals(
                    donation.donation_date, tax_receipt.donation_date)
                self.assertEquals(
                    donation.tax_receipt_total, tax_receipt.amount)

    def test_donation_2(self):
        self.donation_id = self.ddo.create({
            'check_total': 1000,
            'partner_id': self.donor1.id,
            'donation_date': time.strftime('%Y-%m-%d'),
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'each',
            'line_ids': [(0, 0, {
                'product_id': self.inkind_product.id,
                'quantity': 1,
                'unit_price': 1000,
                })],
            })
        self.donation_id.name_get()
        self.donation_id.save_default_values()
        self.donation_id.partner_id_change()
        self.donation_id.tax_receipt_option_change()
        self.donation_id.validate()
        self.donation_id.line_ids[0]._compute_amount()
        self.donation_id.line_ids[0].product_id_change()
        self.donation_id.tax_receipt_id = False
        self.donation_id.done2cancel()
        self.donation_id.cancel2draft()
        self.donation_id.unlink()

    def test_annual_tax_receipt(self):
        self.res_partner = self.env['res.partner']

        partner_familly = self.res_partner.create({
            'name': u'Famille Joly',
            'tax_receipt_option': 'annual',
            })
        partner_husband = self.res_partner.create({
            'parent_id': partner_familly.id,
            'name': u'Xavier Joly'})
        partner_wife = self.res_partner.create({
            'parent_id': partner_familly.id,
            'name': u'Stéphanie Joly'})

        partner_husband._compute_donation_count()
        dons = self.create_donation_annual_receipt(
            partner_husband, 40, 10, 'CHQ FB 93283290')
        dons += self.create_donation_annual_receipt(
            partner_husband, 140, 60, 'CHQ FB OPIE02')
        dons += self.create_donation_annual_receipt(
            partner_wife, 20, 5, 'CHQ FB AZERTY1242')
        dons.validate()
        last_day_year = time.strftime('%Y-12-31')
        wizard = self.env['tax.receipt.annual.create'].create({
            'start_date': time.strftime('%Y-01-01'),
            'end_date': last_day_year})
        action = wizard.generate_annual_receipts()
        tax_receipt_ids = action['domain'][0][2]
        self.assertTrue(tax_receipt_ids)
        dtro = self.env['donation.tax.receipt']
        tax_receipts = dtro.search([
            ('partner_id', '=', partner_familly.id),
            ('type', '=', 'annual'),
            ('id', 'in', tax_receipt_ids)])
        self.assertEquals(len(tax_receipts), 1)
        tax_receipt = tax_receipts[0]
        self.assertEquals(tax_receipt.amount, 200)
        self.assertTrue(tax_receipt.number)
        self.assertEquals(
            tax_receipt.date, fields.Date.from_string(last_day_year)
        )
        self.assertEquals(
            tax_receipt.donation_date, fields.Date.from_string(last_day_year)
        )
        self.assertEquals(
            tax_receipt.currency_id, dons[0].company_id.currency_id)

    def test_account(self):
        self.bank_journal.donation_journal_type_change()
        self.donor1._compute_donation_count()
        with self.assertRaises(ValidationError):
            self.bank_journal.type = 'sale'

    def test_donation_campaign(self):
        self.campaign_id = self.env.ref('donation.quest_origin')
        self.campaign_id.name_get()

        self.don8 = self.ddo.create({
            'check_total': 1000,
            'partner_id': self.donor1.id,
            'donation_date': time.strftime('%Y-%m-%d'),
            'journal_id': self.bank_journal.id,
            'tax_receipt_option': 'each',
            'line_ids': [(0, 0, {
                'product_id': self.inkind_product.id,
                'quantity': 1,
                'unit_price': 1000,
                })],
            })

        self.validate = self.env['donation.validate']
        wizard = self.validate.with_context({
            'active_ids': self.don8.ids,
            'active_model': 'donation.donation',
            'picking_type': 'outgoing',
            'active_id': 1
        }).create({})
        wizard.run()

        self.option_switch = self.env['donation.tax.receipt.option.switch']
        wizard = self.option_switch.create({
            'donation_id': self.don8.id,
            'new_tax_receipt_option': 'annual'
        })
        self.don8.tax_receipt_id = False
        wizard.switch()

    def create_donation_annual_receipt(
            self, partner, amount_tax_receipt, amount_no_tax_receipt,
            payment_ref):
        donation = self.ddo.create({
            'journal_id': self.bank_journal.id,
            'partner_id': partner.id,
            'tax_receipt_option': 'annual',
            'donation_date': time.strftime('%Y-01-01'),
            'payment_ref': payment_ref,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 1,
                    'unit_price': amount_tax_receipt,
                    }),
                (0, 0, {
                    'product_id': self.env.ref(
                        'donation_base.product_product_donation_notaxreceipt'
                        ).id,
                    'quantity': 1,
                    'unit_price': amount_no_tax_receipt,
                    }),
                ]
            })
        return donation
