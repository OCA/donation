# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

# This code is mostly used in the OCA module donation_bank_statement_oca
# But it's located in the "donation" module because it can be useful for
# other modules (alternative reconcile interfaces, module compatible with the Enterprise
# reconcile interface, etc.)


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    donation_ids = fields.One2many(
        "donation.donation", "bank_statement_line_id", string="Donations", readonly=True
    )

    def _check_statement_line_donation(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(
                _(
                    "On bank statement line '%s', the partner is required to "
                    "process a donation."
                )
                % self.display_name
            )
        if self.currency_id.compare_amounts(self.amount, 0) <= 0:
            raise UserError(
                _(
                    "On bank statement line '%(line)s', the amount (%(amount)s) "
                    "is negative so it cannot be processed as a donation.",
                    line=self.display_name,
                    amount=format_amount(self.env, self.amount, self.currency_id),
                )
            )
        if not self.company_id.donation_account_id:
            raise UserError(
                _(
                    "The Donation by Credit Transfer Account is not set for company '%s'."
                )
                % self.company_id.display_name
            )

    def _get_payment_mode_donation(self):
        self.ensure_one()
        payment_mode = self.env["account.payment.mode"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("payment_type", "=", "inbound"),
                ("bank_account_link", "=", "fixed"),
                ("fixed_journal_id", "=", self.journal_id.id),
            ],
            limit=1,
        )
        if not payment_mode:
            raise UserError(
                _(
                    "Missing inbound payment mode linked to the bank journal '%s' "
                    "configured with 'Link to Bank Account' set to 'Fixed'."
                )
                % self.journal_id.display_name
            )
        return payment_mode

    def _get_donation_product(self):
        self.ensure_one()
        product = self.company_id.donation_credit_transfer_product_id
        if not product:
            raise UserError(
                _(
                    "Missing Product for Donations via Credit Transfer "
                    "for company '%s'."
                )
                % self.company_id.display_name
            )
        return product

    def _prepare_donation_context(self):
        self.ensure_one()
        product = self._get_donation_product()
        context = {
            "default_company_id": self.company_id.id,
            "default_partner_id": self.partner_id.id,
            "default_currency_id": self.currency_id.id,
            "default_payment_mode_id": self._get_payment_mode_donation().id,
            "default_payment_ref": self.payment_ref,
            "default_donation_date": self.date,
            "default_bank_statement_line_id": self.id,
            "default_check_total": self.amount,
            "default_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": 1,
                        "unit_price": self.amount,
                    },
                )
            ],
        }
        return context

    def _prepare_donation_action(self):
        action = {
            "type": "ir.actions.act_window",
            "name": _("Create Donation from Bank Statement Line"),
            "res_model": "donation.donation",
            "view_mode": "form",
            "view_id": self.env.ref(
                "donation.donation_from_bank_statement_line_form"
            ).id,
            "target": "new",
            "context": self._prepare_donation_context(),
        }
        return action

    def _prepare_donation_counterpart_move_line_vals(self, credit):
        vals = {
            "move_id": self.move_id.id,
            "account_id": self.company_id.donation_account_id.id,
            "partner_id": self.partner_id.id,
            "credit": credit,
            "debit": False,
        }
        return vals
