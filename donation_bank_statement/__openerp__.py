# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Bank Statement module for OpenERP
#    Copyright (C) 2014 Abbaye du Barroux (www.barroux.org)
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
    'name': 'Donation Bank Statement',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Creates donation from unreconciled bank statement lines',
    'description': """
Donation Bank Statement
=======================

This module is designed to handle donation received by credit transfer. After the import of the bank statement, you can start a wizard that will create a donation for each unreconciled bank statement lines affected to a particular account.

It has been developped by brother Bernard and brother Irenee from Barroux Abbey and by Alexis de Lattre from Akretion.
    """,
    'author': 'Barroux Abbey, Akretion',
    'website': 'http://www.barroux.org',
    'depends': ['account_accountant', 'donation'],
    'data': [
        'company_view.xml',
        'bank_statement_view.xml',
        'donation_view.xml',
        ],
    'demo': [],
}
