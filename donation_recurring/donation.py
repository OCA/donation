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

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    recurring_template = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ], string='Recurring Template', copy=False,
        track_visibility='onchange')
    source_recurring_id = fields.Many2one(
        'donation.donation', string='Source Recurring Template',
        states={'done': [('readonly', True)]})
    recurring_donation_ids = fields.One2many(
        'donation.donation', 'source_recurring_id',
        string='Past Recurring Donations', readonly=True, copy=False)

    @api.one
    @api.constrains('recurring_template', 'source_recurring_id', 'state')
    def _check_recurring_donation(self):
        if self.recurring_template and self.state != 'draft':
            raise Warning(
                _("The recurring donation template of '%s' must stay in "
                    "draft state.") % self.partner_id.name)
        if self.source_recurring_id and self.recurring_template:
            raise Warning(
                _("The recurring donation template of '%s' cannot have "
                    "a Source Recurring Template")
                % self.partner_id.name)

    @api.one
    @api.depends('state', 'partner_id', 'move_id', 'recurring_template')
    def _compute_display_name(self):
        if self.state == 'draft':
            if self.recurring_template == 'active':
                name = _('Recurring Donation of %s') % (
                    self.partner_id.name)
            elif self.recurring_template == 'suspended':
                name = _('Suspended Recurring Donation of %s') % (
                    self.partner_id.name)
            else:
                name = _('Draft Donation of %s') % self.partner_id.name
        elif self.state == 'cancel':
            name = _('Cancelled Donation of %s') % self.partner_id.name
        else:
            name = self.number
        self.display_name = name
