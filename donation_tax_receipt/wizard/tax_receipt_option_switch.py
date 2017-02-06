# -*- coding: utf-8 -*-
# © 2017 Barroux Abbey (www.barroux.org)
# © 2017 Akretion France (www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>


from openerp import models, fields, api


class DonationTaxReceiptOptionSwitch(models.TransientModel):
    _name = 'donation.tax.receipt.option.switch'
    _description = 'Switch Donation Tax Receipt Option'

    donation_id = fields.Many2one(
        'donation.donation', string='Donation',
        default=lambda self: self._context.get('active_id'))
    new_tax_receipt_option = fields.Selection([
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Tax Receipt Option', required=True)

    @api.multi
    def switch(self):
        self.ensure_one()
        assert self.donation_id, 'Missing donation'
        assert not self.donation_id.tax_receipt_id,\
            'Already linked to a tax receipt'
        self.donation_id.tax_receipt_option = self.new_tax_receipt_option
        self.donation_id.generate_each_tax_receipt()
        return True
