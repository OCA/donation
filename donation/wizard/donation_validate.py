# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for Odoo
#    Copyright (C) 2014 Barroux Abbey (www.barroux.org)
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

from openerp.osv import orm


class donation_validate(orm.TransientModel):
    _name = 'donation.validate'
    _description = 'Validate Donations'

    def run(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        assert context.get('active_model') == 'donation.donation',\
            'Source model must be donations'
        assert context.get('active_ids'), 'No donation selected'
        for donation_id in context['active_ids']:
            self.pool['donation.donation'].validate(
                cr, uid, [donation_id], context=context)
        return True
