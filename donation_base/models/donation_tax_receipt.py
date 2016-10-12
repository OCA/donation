# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class DonationTaxReceipt(models.Model):
    _name = 'donation.tax.receipt'
    _description = "Tax Receipt for Donations"
    _order = 'id desc'
    _rec_name = 'number'

    number = fields.Char(string='Receipt Number')
    date = fields.Date(
        string='Date', required=True, default=fields.Date.context_today,
        index=True)
    donation_date = fields.Date(string='Donation Date')
    amount = fields.Monetary(
        string='Amount', digits=dp.get_precision('Account'),
        currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True, ondelete='restrict',
        default=lambda self: self.env.user.company_id.currency_id.id)
    partner_id = fields.Many2one(
        'res.partner', string='Donor', required=True, ondelete='restrict',
        domain=[('parent_id', '=', False)], index=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'donation.tax.receipt'))
    print_date = fields.Date(string='Print Date')
    type = fields.Selection([
        ('each', 'One-Time Tax Receipt'),
        ('annual', 'Annual Tax Receipt'),
        ], string='Type', required=True)

    # Maybe we can drop that code with the new seq management on v9
    @api.model
    def create(self, vals=None):
        if vals is None:
            vals = {}
        date = vals.get('donation_date')
        vals['number'] = self.env['ir.sequence'].with_context(
            date=date).next_by_code('donation.tax.receipt')
        return super(DonationTaxReceipt, self).create(vals)

    @api.model
    def update_tax_receipt_annual_dict(
            self, tax_receipt_annual_dict, start_date, end_date, precision):
        '''This method is inherited in donation and donation_sale
        It is called by the tax.receipt.annual.create wizard'''
