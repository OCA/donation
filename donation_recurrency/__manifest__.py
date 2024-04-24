# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Donation Recurrency",
    "summary": "Make recurring donations",
    "version": "16.0.1.0.0",
    "category": "Custom",
    "website": "https://github.com/OCA/donation",
    "author": "Barroux Abbey, Akretion, Odoo Community Association (OCA)",
    "maintainers": ["brendajfa"],
    "license": "AGPL-3",
    "depends": ["base", "donation", "account_payment_mode", "donation_direct_debit"],
    "data": [
        "security/ir.model.access.csv",
        "data/donation_recurrency_sequence.xml",
        "data/donation_cron.xml",
        "views/donation_recurrency.xml",
        "views/donation_terminate_reason.xml",
        "views/donation.xml",
        "wizards/donation_recurrency_terminate.xml",
    ],
}
