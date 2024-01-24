# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    donation_account_id = fields.Many2one(
        "account.account",
        check_company=True,
        copy=False,
        ondelete="restrict",
        domain="[('reconcile', '=', True), ('deprecated', '=', False), "
        "('company_id', '=', company_id), "
        "('id', 'not in', (default_account_id, suspense_account_id, "
        "payment_credit_account_id, payment_debit_account_id))]",
        string="Donation by Credit Transfer Account",
        help="Transfer account for donations received by credit transfer. "
        "Leave empty if you don't receive donations on this bank account.",
    )

    @api.constrains("donation_account_id")
    def _check_donation_accounts(self):
        for journal in self:
            if (
                journal.donation_account_id
                and not journal.donation_account_id.reconcile
            ):
                raise ValidationError(
                    _(
                        "The Donation by Credit Transfer Account of journal "
                        "'%(journal)s' must be reconciliable, but the account "
                        "'%(account)s' is not reconciliable.",
                        journal=journal.display_name,
                        account=journal.donation_account_id.display_name,
                    )
                )
