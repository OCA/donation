# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import time


class TestDonation(TransactionCase):

    def test_donation(self):
        for i in range(1, 6):
            donation = self.env.ref('donation.donation%d' % i)
            self.assertEquals(donation.state, 'draft')
            donation.validate()
            self.assertEquals(donation.state, 'done')
            if i == 4:  # full in-kind donation
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

    def test_annual_tax_receipt(self):
        partner_familly = self.env['res.partner'].create({
            'name': u'Famille Joly',
            'tax_receipt_option': 'annual',
            })
        partner_husband = self.env['res.partner'].create({
            'parent_id': partner_familly.id,
            'name': u'Xavier Joly'})
        partner_wife = self.env['res.partner'].create({
            'parent_id': partner_familly.id,
            'name': u'Stéphanie Joly'})

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

        self.assertEquals(tax_receipt.date, last_day_year)
        self.assertEquals(tax_receipt.donation_date, last_day_year)
        self.assertEquals(
            tax_receipt.currency_id, dons[0].company_id.currency_id)

    def create_donation_annual_receipt(
            self, partner, amount_tax_receipt, amount_no_tax_receipt,
            payment_ref):
        journal = self.env['account.journal'].search([(
            'type', '=', 'bank')], limit=1)
        donation = self.env['donation.donation'].create({
            'journal_id': journal.id,
            'partner_id': partner.id,
            'currency_id': self.env.ref('base.main_company').currency_id.id,
            'tax_receipt_option': 'annual',
            'donation_date': time.strftime('%Y-01-01'),
            'payment_ref': payment_ref,
            'line_ids': [
                (0, 0, {
                    'product_id':
                    self.env.ref('donation_base.product_product_donation').id,
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
