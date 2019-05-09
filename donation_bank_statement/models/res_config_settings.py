# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    donation_credit_transfer_journal_id = fields.Many2one(
        'account.journal',
        related='company_id.donation_credit_transfer_journal_id')
    donation_credit_transfer_product_id = fields.Many2one(
        'product.product',
        related='company_id.donation_credit_transfer_product_id')
