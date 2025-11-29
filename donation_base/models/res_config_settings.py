# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    split_by_payment_mode = fields.Boolean(
        string="Split Donation Receipts by Payment Mode",
        related="company_id.donation_receipt_split_by_payment_mode",
        readonly=False)