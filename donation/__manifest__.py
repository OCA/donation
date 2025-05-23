# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Donation",
    "version": "14.0.1.8.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Manage donations",
    "author": "Barroux Abbey, Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": ["donation_base", "account_payment_mode"],
    "data": [
        "security/donation_security.xml",
        "security/ir.model.access.csv",
        "wizard/tax_receipt_option_switch_view.xml",
        "wizard/donation_validate_view.xml",
        "views/donation_tax_receipt.xml",
        "views/donation.xml",
        "wizard/res_config_settings.xml",
        "data/donation_sequence.xml",
        "views/account_payment_mode.xml",
        "views/account_bank_statement.xml",
        "views/donation_campaign.xml",
        "views/donation_thanks_template.xml",
        "views/res_users.xml",
        "views/res_partner.xml",
        "views/account_journal.xml",
        "report/donation_report_view.xml",
        "report/donation_thanks_view.xml",
        "report/donation_thanks_report.xml",
    ],
    "post_init_hook": "update_account_payment_mode",
    "demo": ["demo/donation_demo.xml"],
    "installable": True,
}
