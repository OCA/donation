# -*- coding: utf-8 -*-
# © 2015-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Donation Direct Debit',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Auto-generate direct debit order on donation validation',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account_banking_sepa_direct_debit', 'donation'],
    'data': [
        'donation_view.xml',
        'security/ir.model.access.csv',
        ],
    'demo': ['donation_demo.xml'],
    'installable': True,
}
