# -*- coding: utf-8 -*-
# © 2016 La Cimade (http://www.lacimade.org/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation Sale',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage donations in sale orders',
    'author': 'La Cimade, Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/donation',
    'depends': [
        'donation_base',
        'sale_management'
    ],
    'data': [
        'data/cron.xml',
        'views/account_invoice.xml',
        'views/sale_order.xml',
        'views/donation_tax.xml',
    ],
    'installable': True,
}
