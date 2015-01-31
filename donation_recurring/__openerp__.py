# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring module for Odoo
#    Copyright (C) 2014 Abbaye du Barroux
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Donation Recurring',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage recurring donations',
    'description': """
Donation Recurring
==================

This module handles recurring donations. For example, if you have
setup a donation plan where donors can donate monthly via direct
debit, you can use this module in combination with the module
account_banking_sepa_direct_debit to organise your recurring donations.

It has been developped by brother Bernard and brother Irenee from
Barroux Abbey and by Alexis de Lattre from Akretion.
    """,
    'author': 'Barroux, Akretion',
    'website': 'http://www.barroux.org',
    'depends': ['donation'],
    'data': [
        'donation_view.xml',
        'wizard/donation_recurring_generate_view.xml',
        ],
    'demo': ['donation_recurring_demo.xml'],
    'test': ['test/generate_recurring_donations.yml'],
}
