# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    donation_credit_transfer_product_id = fields.Many2one(
        related="company_id.donation_credit_transfer_product_id", readonly=False
    )
    donation_account_id = fields.Many2one(
        related="company_id.donation_account_id",
        readonly=False,
        domain="[('reconcile', '=', True), ('deprecated', '=', False), "
        "('company_id', '=', company_id), ('account_type', '=', 'asset_current')]",
    )
    group_donation_check_total = fields.Boolean(
        string="Check Total on Donations",
        implied_group="donation.group_donation_check_total",
    )
