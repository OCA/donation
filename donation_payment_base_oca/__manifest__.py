# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Donation Payment Base OCA",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Glue module between donation and account_payment_base_oca",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": [
        "donation",
        "account_payment_base_oca",
    ],
    "data": [
        "views/account_payment_method_line.xml",
    ],
    "installable": True,
    "auto_install": True,
}
