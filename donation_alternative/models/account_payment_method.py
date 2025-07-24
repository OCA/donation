# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.method.line"

    donation = fields.Boolean(
        help="If enabled, this payment mode will be available on donations",
    )

    @api.constrains("donation")
    def _check_donation(self):
        for mode in self:
            if mode.donation and mode.payment_type != "inbound":
                raise ValidationError(
                    _(
                        f"Donation payment mode '{mode.name}'"
                        "is not an inbound payment mode."
                    )
                )
            if mode.donation and mode.bank_account_link != "fixed":
                raise ValidationError(
                    _(
                        f"Donation payment mode '{mode.names}' must be configured with "
                        "'Link to Bank Account' set to 'Fixed'."
                    )
                )

    @api.onchange("donation")
    def donation_change(self):
        if self.donation and self.bank_account_link != "fixed":
            self.bank_account_link = "fixed"
