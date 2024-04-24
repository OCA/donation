# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Donation Thanks Letter",
    "summary": "Donation Thanks Letter",
    "version": "16.0.1.0.0",
    "category": "Custom",
    "website": "https://github.com/OCA/donation",
    "author": "Barroux Abbey, Akretion, Odoo Community Association (OCA)",
    "maintainers": ["brendajfa"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["donation", "account", "mail", "donation_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "views/donation_letter_send_views.xml",
        "views/donation_send_button.xml",
    ],
}
