# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Donation Summary",
    "summary": "Make summary donations",
    "version": "16.0.1.0.0",
    "category": "Custom",
    "website": "https://github.com/OCA/donation",
    "author": "Barroux Abbey, Akretion, Odoo Community Association (OCA)",
    "maintainers": ["brendajfa"],
    "license": "AGPL-3",
    "depends": ["donation", "donation_base", "mail", "donation_certificate"],
    "data": [
        "report/donation_summary.xml",
        "report/donation_summary_templates.xml",
        "views/donation_summary_views.xml",
        "views/donation_summary_send_views.xml",
        "data/mail_template.xml",
    ],
}
