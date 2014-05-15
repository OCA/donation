# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for OpenERP
#    Copyright (C) 2014 Abbaye du Barroux
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
    'name': 'Donation',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage donations',
    'description': """
Donation
========

This module handles donations.

It has been developped by brother Bernard and brother Irenee from Barroux Abbey and by Alexis de Lattre from Akretion.
    """,
    'author': 'Barroux, Akretion',
    'website': 'http://www.barroux.org',
    'depends': ['account_accountant'],
    'data': [
        'security/donation_security.xml',
        'donation_view.xml',
        'donation_data.xml',
        'product_view.xml',
        'donation_campaign_view.xml',
        'campaign_user_view.xml',
        'security/ir.model.access.csv',
        ],
    'demo': [
        'product_demo.xml',
        'donation_demo.xml',
        ],
    'active': False,
}