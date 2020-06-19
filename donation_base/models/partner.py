# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tax_receipt_option = fields.Selection([
        ('none', 'None'),
        ('each', 'For Each Donation'),
        ('annual', 'Annual Tax Receipt')],
        string='Tax Receipt Option',
        default='each',
        track_visibility='onchange'
    )
    tax_receipt_ids = fields.One2many(
        'donation.tax.receipt',
        'partner_id',
        string='Tax Receipts'
    )
    tax_receipt_count = fields.Integer(
        compute='_compute_tax_receipt_count',
        string="# of Tax Receipts",
        readonly=True
    )
    donor = fields.Boolean(string='Donor')

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res.append('tax_receipt_option')
        return res

    @api.depends('tax_receipt_ids')
    def _compute_tax_receipt_count(self):
        for partner in self:
            partner.tax_receipt_count = len(partner.tax_receipt_ids.ids)
