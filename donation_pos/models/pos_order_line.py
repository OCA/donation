from odoo import fields, models


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    donation = fields.Boolean(
        string="Donation",
    )
