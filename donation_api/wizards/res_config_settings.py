# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    donation_controller_company_id = fields.Many2one(
        "res.company",
        config_parameter="donation.controller.company_id",
        string="Default Company for Donations created from Web Form",
    )
