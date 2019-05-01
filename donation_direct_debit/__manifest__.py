# © 2015-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation Direct Debit',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Auto-generate direct debit order on donation validation',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': [
        'account_banking_sepa_direct_debit',
        'donation'
    ],
    'contributors': [
        'Thore Baden',
        'Alexis de Lattre',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/donation_view.xml',
    ],
    'demo': [
        'demo/donation_demo.xml'
    ],
    'installable': True,
}
