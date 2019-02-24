# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation Thanks',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Create thanks letter for a donation',
    'author': 'Barroux Abbey,Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.barroux.org',
    'depends': ['donation', 'report_py3o'],
    'data': [
        'security/donation_security.xml',
        'security/ir.model.access.csv',
        'report/report_thanks.xml',
        'views/donation.xml',
        'views/donation_thanks_template.xml',
        ],
    'installable': True,
}
