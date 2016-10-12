# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation Bank Statement',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Creates donation from unreconciled bank statement lines',
    'author': 'Barroux Abbey, Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.barroux.org',
    'depends': ['donation'],
    'data': [
        'views/company.xml',
        'views/bank_statement.xml',
        'views/donation.xml',
        'security/ir.model.access.csv',
        ],
    'demo': ['demo/demo.xml'],
    'installable': True,
}
