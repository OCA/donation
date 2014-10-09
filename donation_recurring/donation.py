# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring module for Odoo
#    Copyright (C) 2014 Artisanat Monastique de Provence www.barroux.org
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class donation_donation(orm.Model):
    _inherit = 'donation.donation'

    _columns = {
        'recurring_template': fields.selection([
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ], 'Recurring Template', copy=False),
        'source_recurring_id': fields.many2one(
            'donation.donation', 'Source Recurring Template',
            states={'done': [('readonly', True)]}),
        'recurring_donation_ids': fields.one2many(
            'donation.donation', 'source_recurring_id',
            'Past Recurring Donations', readonly=True, copy=False),
        }

    def _check_recurring_donation(self, cr, uid, ids):
        for donation in self.browse(cr, uid, ids):
            if donation.recurring_template and donation.state != 'draft':
                raise orm.except_orm(
                    _('Error:'),
                    _("The recurring donation template of '%s' must stay in "
                        "draft state.") % donation.partner_id.name)
            if donation.source_recurring_id and donation.recurring_template:
                raise orm.except_orm(
                    _('Error:'),
                    _("The recurring donation template of '%s' cannot have "
                        "a Source Recurring Template")
                    % donation.partner_id.name)
        return True

    _constraints = [
        (_check_recurring_donation, 'Configuration Error in Recurring Donations', ['recurring_template', 'state']),
    ]
