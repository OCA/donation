# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class DonationLine(models.Model):
    _inherit = "donation.line"

    donation_date = fields.Date(related="donation_id.donation_date", store=True)
