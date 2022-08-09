# © 2022 KMEE INFORMATICA LTDA (https://kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    use_auto_contribution = fields.Boolean(
        string="Use automatic contribution",
        help=(
            "Automatically adds the configured contribution to the POS order."
            " Contributions can later be changed or removed in the payment screen."
        ),
        default=False,
    )

    suggested_contribution_add_to_total = fields.Boolean(
        string="Suggested contribution added to total?",
        help=(
            "If checked contribution will add to POS order total. If not it will only"
            " show up in the payment screen."
        ),
        default=True,
    )

    display_subtotal_without_donation = fields.Boolean(
        string="Display subtotal without donation?",
        help=(
            "If contribution is added to total and this field is checked: an additional"
            " subtotal line will be added to help the customer identify each price."
        ),
        default=True,
    )

    auto_contribution_mode = fields.Selection(
        string="Auto Contribution Mode",
        selection=[("fixed", "Fixed Value"), ("percentage", "Order Percentage")],
        default="percentage",
    )

    contribution_default_fixed_value = fields.Float(
        string="Default fixed value",
    )

    contribution_default_percentage_value = fields.Float(
        string="Default percentage value",
    )

    default_donation_product_id = fields.Many2one(
        string="Default Donation Product",
        comodel_name="product.product",
        ondelete="restrict",
    )
