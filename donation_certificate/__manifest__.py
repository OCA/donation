# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Donation Certificate",
    "summary": "Donation Certificate",
    "version": "16.0.1.0.0",
    "category": "Custom",
    "website": "https://github.com/OCA/donation",
    "author": "Brenda Fernández Alayo",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": ["report_py3o", "donation", "donation_base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/donation_sequence.xml",
        "data/py3o_certificate_template.xml",
        "views/donation_certificate_send_views.xml",
        "views/tax_receipt_donation.xml",
        "views/donation_send_cert_button.xml",
        "views/py3o_certificate_report.xml",
        "wizard/tax_receipt_annual_create_view.xml",
        "wizard/tax_receipt_print_view.xml",
    ],
}
