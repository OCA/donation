# Copyright 2023 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Donation Bank Statement OCA",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Manage donations by credit transfer",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": ["donation", "account_reconcile_oca"],
    "data": [
        "views/account_bank_statement_line.xml",
    ],
    "installable": True,
    "auto_install": True,
}
