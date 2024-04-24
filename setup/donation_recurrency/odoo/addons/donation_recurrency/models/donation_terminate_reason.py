# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DonationTerminateReason(models.Model):

    _name = "donation.terminate.reason"
    _description = "Donation Termination Reason"

    name = fields.Char(required=True)
    terminate_comment_required = fields.Boolean(
        string="Require a termination comment", default=True
    )
