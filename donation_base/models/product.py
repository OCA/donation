# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    donation_type = fields.Selection(
        selection=[
            ("donation", "Monetary Donation"),
            ("donation_in_kind", "In-Kind Donation"),
        ],
        string="Donation",
    )
    tax_receipt_ok = fields.Boolean(
        string="Is Eligible for a Tax Receipt",
        tracking=True,
        compute="_compute_tax_receipt_ok",
        readonly=False,
        store=True,
        precompute=True,
        help="Specify if the product is eligible for a tax receipt",
    )

    @api.depends("donation_type")
    def _compute_tax_receipt_ok(self):
        for product in self:
            if not product.donation_type:
                product.tax_receipt_ok = False

    @api.onchange("donation_type")
    def _donation_change(self):
        for product in self:
            if product.donation_type:
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False

    @api.constrains("donation_type", "taxes_id")
    def donation_check(self):
        for product in self:
            # The check below is to make sure that we don't forget to remove
            # the default sale VAT tax on the donation product, particularly
            # for users of donation_sale. If there are countries that have
            # sale tax on donations (!), please tell us and we can remove this
            # constraint
            if product.donation_type and product.taxes_id:
                raise ValidationError(
                    _(
                        "There shouldn't have any Customer Taxes on the "
                        "donation product '%s'."
                    )
                    % product.display_name
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("donation_type")
    def _donation_change(self):
        for product in self:
            if product.donation_type:
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False
