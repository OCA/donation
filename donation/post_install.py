# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def update_account_payment_method_line(env):
    modes = env["account.payment.method.line"].search(
        [("payment_type", "=", "inbound")]
    )
    modes.write({"donation": True})
