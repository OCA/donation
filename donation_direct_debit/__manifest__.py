# Copyright 2015-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Donation Direct Debit",
    "version": "16.0.2.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Auto-generate direct debit order on donation validation",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": ["account_banking_sepa_direct_debit", "donation"],
    "data": [
        "views/donation.xml",
        "wizards/res_config_settings.xml",
    ],
    "demo": ["demo/donation_demo.xml"],
    "installable": True,
}
