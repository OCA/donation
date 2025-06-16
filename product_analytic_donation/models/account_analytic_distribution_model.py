# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    @api.model
    def _get_distribution(self, vals):
        res = super()._get_distribution(vals)
        if res:
            return res
        if vals.get("product_id") and self.env.context.get("default_donation"):
            product = self.env["product.product"].browse(vals["product_id"])
            ana_account_dict = product.product_tmpl_id._get_product_analytic_accounts()
            ana_account = ana_account_dict["income"]
            if ana_account:
                res = {ana_account.id: 100}
        return res
