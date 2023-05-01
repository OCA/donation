# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def donation_reconcile_bank_line(self):
        self.ensure_one()
        journal = self.journal_id
        if journal.reconcile_mode != "edit":
            raise UserError(
                _(
                    "The reconcile mode of the bank journal '%(journal)s' is "
                    "'%(reconcile_mode)s'. For donations, the only supported "
                    "reconcile mode is 'Edit'.",
                    journal=journal.display_name,
                    reconcile_mode=journal._fields["reconcile_mode"].convert_to_export(
                        journal.reconcile_mode, journal
                    ),
                )
            )
        self._check_statement_line_donation()
        self.reconcile_mode = self.journal_id.reconcile_mode
        return getattr(self, "_donation_reconcile_bank_line_%s" % self.reconcile_mode)(
            self.reconcile_data_info["data"]
        )

    def _donation_reconcile_bank_line_edit(self, data):
        _liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()
        lines_to_remove = [(2, line.id) for line in suspense_lines + other_lines]

        # Cleanup previous lines.
        move = self.move_id
        container = {"records": move, "self": move}
        with move._check_balanced(container):
            move.with_context(
                skip_account_move_synchronization=True,
                force_delete=True,
                skip_invoice_sync=True,
            ).write({"line_ids": lines_to_remove})
            # create counter-part
            vals = self._prepare_donation_counterpart_move_line_vals(
                _liquidity_lines.debit
            )
            self.env["account.move.line"].with_context(
                check_move_validity=False,
                skip_sync_invoice=True,
                skip_invoice_sync=True,
            ).create(vals)
        action = self._prepare_donation_action()
        return action
