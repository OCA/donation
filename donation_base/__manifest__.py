# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation Base',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Base module for donations',
    'author': 'Barroux Abbey, Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/donation',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/tax_receipt_security.xml',
        'views/product.xml',
        'views/partner.xml',
        'views/donation_tax_receipt.xml',
        'wizard/tax_receipt_annual_create_view.xml',
        'wizard/tax_receipt_print_view.xml',
        'report/report.xml',
        'report/report_donationtax.xml',
        'data/donation_tax_seq.xml',
        'data/donation_mail_template.xml',
    ],
    'demo': [
        'demo/donation_demo.xml',
    ],
    'installable': True,
}
