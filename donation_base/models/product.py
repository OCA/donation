# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection(
        selection_add=[
            ("donation", "Donation"),
            ("donation_in_kind_consu", "In-Kind Donation Consummable"),
            ("donation_in_kind_service", "In-Kind Donation Service"),
        ],
        ondelete={
            "donation": "set service",
            "donation_in_kind_consu": "set consu",
            "donation_in_kind_service": "set service",
        },
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

    @api.depends("detailed_type")
    def _compute_tax_receipt_ok(self):
        for product in self:
            if product.detailed_type and not product.detailed_type.startswith(
                "donation"
            ):
                product.tax_receipt_ok = False

    def _detailed_type_mapping(self):
        res = super()._detailed_type_mapping()
        res.update(
            {
                "donation": "service",
                "donation_in_kind_consu": "consu",
                "donation_in_kind_service": "service",
            }
        )
        return res

    @api.onchange("detailed_type")
    def _donation_change(self):
        for product in self:
            if product.detailed_type == "donation":
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False

    @api.constrains("detailed_type", "taxes_id")
    def donation_check(self):
        for product in self:
            # The check below is to make sure that we don't forget to remove
            # the default sale VAT tax on the donation product, particularly
            # for users of donation_sale. If there are countries that have
            # sale tax on donations (!), please tell us and we can remove this
            # constraint
            if product.detailed_type == "donation" and product.taxes_id:
                raise ValidationError(
                    _(
                        "There shouldn't have any Customer Taxes on the "
                        "donation product '%s'."
                    )
                    % product.display_name
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("detailed_type")
    def _donation_change(self):
        for product in self:
            if product.detailed_type == "donation":
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False
