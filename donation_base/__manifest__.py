# © 2014-2021 Barroux Abbey (http://www.barroux.org)
# © 2014-2021 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Donation Base",
    "version": "16.0.2.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Base module for donations",
    "author": "Barroux Abbey, Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "security/tax_receipt_security.xml",
        "report/report.xml",
        "views/product.xml",
        "views/res_partner.xml",
        "views/donation_tax_receipt.xml",
        "wizard/tax_receipt_annual_create_view.xml",
        "wizard/tax_receipt_print_view.xml",
        "report/report_donationtax.xml",
        "data/donation_tax_seq.xml",
        "data/donation_mail_template.xml",
    ],
    "demo": ["demo/donation_demo.xml"],
    "installable": True,
}
