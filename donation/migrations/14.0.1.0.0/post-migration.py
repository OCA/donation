# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    journal2pay_mode = {}
    for pay_mode in env["account.payment.mode"].search(
        [
            ("payment_type", "=", "inbound"),
            ("bank_account_link", "=", "fixed"),
            ("fixed_journal_id", "!=", False),
        ]
    ):
        journal2pay_mode[pay_mode.fixed_journal_id.id] = pay_mode.id

    for journal_id, payment_mode_id in journal2pay_mode.items():
        sql = (
            "UPDATE donation_donation SET payment_mode_id=%%s "
            "WHERE %(journal_field)s=%%s"
            % {"journal_field": openupgrade.get_legacy_name("journal_id")}
        )
        openupgrade.logged_query(env.cr, sql, (payment_mode_id, journal_id))
        pay_mode_sql = "UPDATE account_payment_mode SET donation=true WHERE id=%s"
        openupgrade.logged_query(env.cr, pay_mode_sql, (payment_mode_id,))
