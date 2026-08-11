# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    donation_receipt_split_by_payment_mode = fields.Boolean(
        string="Split Donation Receipts by Payment Mode",
        help="If enabled, annual donation tax receipts will be split by payment mode. "
        "If disabled, one annual donation tax receipt will be generated per donor, "
        "regardless of the payment mode used.",
    )