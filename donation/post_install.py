# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def update_account_payment_mode(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        modes = env["account.payment.mode"].search(
            [("payment_type", "=", "inbound"), ("bank_account_link", "=", "fixed")]
        )
        modes.write({"donation": True})
    return
