# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
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
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage recurring donations',
    'author': 'Barroux Abbey, Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.barroux.org',
    'depends': ['donation'],
    'data': [
        'donation_view.xml',
        'wizard/donation_recurring_generate_view.xml',
        ],
    'demo': ['donation_recurring_demo.xml'],
    'test': ['test/generate_recurring_donations.yml'],
}
