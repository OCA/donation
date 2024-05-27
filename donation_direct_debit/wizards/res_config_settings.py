# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    donation_debit_order_account_id = fields.Many2one(
        related="company_id.donation_debit_order_account_id",
        readonly=False,
        domain="[('reconcile', '=', True), ('deprecated', '=', False), "
        "('company_id', '=', company_id), "
        "('account_type', '=', 'asset_receivable')]",
    )
