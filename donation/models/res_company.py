# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    donation_credit_transfer_product_id = fields.Many2one(
        "product.product",
        string="Product for Donations via Credit Transfer",
        domain=[("detailed_type", "=", "donation")],
        ondelete="restrict",
    )
    donation_account_id = fields.Many2one(
        "account.account",
        check_company=True,
        copy=False,
        ondelete="restrict",
        string="Donation by Credit Transfer Account",
        help="Transfer account for donations received by credit transfer. ",
    )

    @api.constrains("donation_credit_transfer_product_id")
    def company_donation_bank_statement_check(self):
        for company in self:
            product = company.donation_credit_transfer_product_id
            if product and product.detailed_type != "donation":
                raise ValidationError(
                    _(
                        "On the company %(company)s, the Product for Donations "
                        "via Credit Transfer (%(product)s) is not a donation product !",
                        company=company.display_name,
                        product=product.display_name,
                    )
                )
