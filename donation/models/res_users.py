# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # begin with context_ to allow user to change it by himself
    context_donation_campaign_id = fields.Many2one(
        "donation.campaign", "Current Donation Campaign"
    )
    context_donation_payment_mode_id = fields.Many2one(
        "account.payment.mode",
        "Current Donation Payment Mode",
        domain=[("donation", "=", True)],
        company_dependent=True,
    )
