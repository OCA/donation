# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Direct Debit module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Donation Direct Debit',
    'version': '8.0.0.1.0',
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
    'test': ['test/direct_debit.yml'],
    'installable': True,
}
