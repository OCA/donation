# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring module for Odoo
#    Copyright (C) 2014 Artisanat Monastique de Provence www.barroux.org
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#    @author: Brother Bernard <informatique@barroux.org>
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

from openerp.osv import orm, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class donation_recurring_generate(orm.TransientModel):
    _name = 'donation.recurring.generate'
    _description = 'Generate Recurring Donations'

    _columns = {
        'date': fields.date('Date', required=True),
        'payment_ref': fields.char('Payment Reference', size=32),
    }

    _defaults = {
        'date': fields.date.context_today,
        }

    def generate(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'only one ID allowed here'
        wiz = self.browse(cr, uid, ids[0], context=context)
        doo = self.pool['donation.donation']
        donation_ids = doo.search(
            cr, uid, [
                ('recurring_template', '=', 'active')], context=context)
        new_donation_ids = []
        for donation_id in donation_ids:
            # Move to dedicated function ?
            default = {
                'donation_date': wiz.date,
                'source_recurring_id': donation_id,
                'payment_ref': wiz.payment_ref,
            }
            new_donation_id = doo.copy(
                cr, uid, donation_id, default=default, context=context)
            new_donation_ids.append(new_donation_id)
        action_id = self.pool['ir.model.data'].xmlid_to_res_id(
            cr, uid, 'donation.donation_action', raise_if_not_found=True)
        action = self.pool['ir.actions.act_window'].read(
            cr, uid, action_id, context=context)
        action.update({
            'view_mode': 'tree,form,graph',
            'domain': [('id', 'in', new_donation_ids)],
            'target': 'current',
            'limit': 500,
            })
        print "action=", action
        return action
