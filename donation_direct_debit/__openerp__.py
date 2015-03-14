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
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Auto-generate direct debit order on donation validation',
    'description': """
Donation Direct Debit
=====================

With this module, when you validate a donation that has a payment method linked to a SEPA direct debit payment mode :

* if a draft direct debit order for SEPA Direct Debit already exists, a new payment line is added to it for that donation,

* otherwise, a new SEPA direct debit order is created for this donation.

This module has been written by Alexis de Lattre from Akretion <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['account_banking_sepa_direct_debit', 'donation'],
    'data': ['donation_view.xml'],
    'installable': True,
}
