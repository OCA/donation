# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_renames = {
    "donation_donation": [("journal_id", None)],
}


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "res_users", "context_donation_payment_mode_id"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "context_donation_payment_mode_id",
                    "res.users",
                    "res_users",
                    "many2one",
                    False,
                    "donation",
                )
            ],
        )
        openupgrade.drop_columns(
            env.cr, [("res_users", "context_donation_payment_mode_id")]
        )
    openupgrade.rename_columns(env.cr, column_renames)
