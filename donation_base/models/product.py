# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    donation = fields.Boolean(string="Is a Donation", tracking=True)
    in_kind_donation = fields.Boolean(string="In-Kind Donation", tracking=True)
    tax_receipt_ok = fields.Boolean(
        string="Is Eligible for a Tax Receipt",
        tracking=True,
        help="Specify if the product is eligible for a tax receipt",
    )

    @api.onchange("donation")
    def _donation_change(self):
        for product in self:
            if product.donation and not product.in_kind_donation:
                product.type = "service"
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False
            if not product.donation:
                product.tax_receipt_ok = False
                product.in_kind_donation = False

    @api.constrains("donation", "type")
    def donation_check(self):
        for product in self:
            if product.in_kind_donation and not product.donation:
                raise ValidationError(
                    _(
                        "The option 'In-Kind Donation' is active on "
                        "the product '%s', so you must also activate the "
                        "option 'Is a Donation'."
                    )
                    % product.display_name
                )
            if product.tax_receipt_ok and not product.donation:
                raise ValidationError(
                    _(
                        "The option 'Is Eligible for a Tax Receipt' is "
                        "active on the product '%s', so you must also activate "
                        "the option 'Is a Donation'."
                    )
                    % product.display_name
                )
            # The check below is to make sure that we don't forget to remove
            # the default sale VAT tax on the donation product, particularly
            # for users of donation_sale. If there are countries that have
            # sale tax on donations (!), please tell us and we can remove this
            # constraint
            if product.donation and product.taxes_id:
                raise ValidationError(
                    _(
                        "There shouldn't have any Customer Taxes on the "
                        "donation product '%s'."
                    )
                    % product.display_name
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("donation")
    def _donation_change(self):
        for product in self:
            if product.donation and not product.in_kind_donation:
                product.type = "service"
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False
            if not product.donation:
                product.tax_receipt_ok = False
                product.in_kind_donation = False
