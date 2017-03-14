# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Donation Tax Receipt',
    'version': '8.0.0.2.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage tax receipts for donations',
    'author': 'Barroux Abbey, Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.barroux.org',
    'depends': ['donation', 'account_auto_fy_sequence'],
    'data': [
        'wizard/tax_receipt_option_switch_view.xml',
        'donation_tax_view.xml',
        'donation_tax_data.xml',
        'partner_view.xml',
        'product_view.xml',
        'security/ir.model.access.csv',
        'wizard/tax_receipt_print_view.xml',
        'wizard/tax_receipt_annual_create_view.xml',
        'report.xml',
        'report/report_donationtax.xml',
        'report/donation_report_view.xml',
        'security/tax_receipt_security.xml',
        ],
    'demo': ['donation_tax_demo.xml'],
    'test': [
        'test/each_tax_receipt.yml',
        'test/annual_tax_receipt.yml',
        ],
}
