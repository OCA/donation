# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestDonationRecurring(TransactionCase):

    def test_donation_recurring(self):
        wizard = self.env['donation.recurring.generate'].create(
            {'payment_ref': 'Don Abbaye Sainte Madeleine'})
        action = wizard.generate()
        active_don_recs = [
            self.env.ref('donation_recurring.donation_rec1'),
            self.env.ref('donation_recurring.donation_rec2')]
        for don_rec in active_don_recs:
            self.assertTrue(don_rec.recurring_donation_ids)
            don = don_rec.recurring_donation_ids[0]
            self.assertEquals(don.state, 'draft')
            self.assertEquals(don.amount_total, don_rec.amount_total)
            self.assertEquals(
                don.payment_ref,
                'Don Abbaye Sainte Madeleine')
            self.assertEquals(don.campaign_id, don_rec.campaign_id)
        don_rec3 = self.env.ref('donation_recurring.donation_rec3')
        self.assertFalse(don_rec3.recurring_donation_ids)
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
