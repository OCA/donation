# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
            raise UserError(
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
