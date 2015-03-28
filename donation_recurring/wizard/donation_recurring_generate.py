# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class DonationRecurringGenerate(models.TransientModel):
    _name = 'donation.recurring.generate'
    _description = 'Generate Recurring Donations'
    _rec_name = 'date'

    date = fields.Date(required=True, default=fields.Date.context_today)
    payment_ref = fields.Char(string='Payment Reference', size=32)

    @api.model
    def _prepare_donation_default(self, donation):
        default = {
            'donation_date': self.date,
            'source_recurring_id': donation.id,
            'payment_ref': self.payment_ref,
            }
        return default

    @api.multi
    def generate(self):
        self.ensure_one()
        doo = self.env['donation.donation']
        donations = doo.search([
            ('recurring_template', '=', 'active'),
            ('company_id', '=', self.env.user.company_id.id)])
        new_donation_ids = []
        existing_recur_donations = doo.search([
            ('donation_date', '=', self.date),
            ('source_recurring_id', '!=', False),
            ('company_id', '=', self.env.user.company_id.id)])
        if existing_recur_donations:
            raise Warning(
                _('Recurring donations have already been generated for %s.')
                % self.date)
        for donation in donations:
            default = self._prepare_donation_default(donation)
            new_donation = donation.copy(default=default)
            new_donation_ids.append(new_donation.id)
        action = self.env.ref('donation.donation_action').read()[0]
        action.update({
            'view_mode': 'tree,form,graph',
            'domain': [('id', 'in', new_donation_ids)],
            'target': 'current',
            'limit': 500,
            })
        return action
