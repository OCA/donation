# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    donation_debit_order_account_id = fields.Many2one(
        "account.account",
        check_company=True,
        copy=False,
        ondelete="restrict",
        # domain is in res.config.settings
        # domain="[('reconcile', '=', True), ('deprecated', '=', False), "
        # "('company_id', '=', company_id), "
        # "('account_type', '=', 'asset_receivable'), "
        # "('id', 'not in', (default_account_id, suspense_account_id))]",
        string="Donation by Debit Order Account",
        help="Transfer account for donations by debit order. "
        "Leave empty if you don't handle donations by debit order on this bank account."
        "This account must be a receivable account, otherwise the debit order will not work.",
    )

    @api.constrains("donation_debit_order_account_id")
    def _check_donation_accounts(self):
        acc_type2label = dict(
            self.env["account.account"].fields_get("account_type", "selection")[
                "account_type"
            ]["selection"]
        )
        for company in self:
            ddo_account = company.donation_debit_order_account_id
            if ddo_account:
                if not ddo_account.reconcile:
                    raise ValidationError(
                        _(
                            "The Donation by Debit Order Account of company "
                            "'%(company)s' must be reconciliable, but the account "
                            "'%(account)s' is not reconciliable.",
                            company=company.display_name,
                            account=ddo_account.display_name,
                        )
                    )
                if ddo_account.account_type != "asset_receivable":
                    raise ValidationError(
                        _(
                            "The Donation by Debit Order Account of company "
                            "'%(company)s' must be a receivable account, "
                            "but the account '%(account)s' is configured with "
                            "account type '%(account_type)s'.",
                            company=company.display_name,
                            account=ddo_account.display_name,
                            account_type=acc_type2label[ddo_account.account_type],
                        )
                    )
