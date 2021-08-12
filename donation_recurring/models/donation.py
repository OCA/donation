# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    recurring_template = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ], string='Recurring Template', copy=False, index=True,
        track_visibility='onchange')
    source_recurring_id = fields.Many2one(
        'donation.donation', string='Source Recurring Template',
        states={'done': [('readonly', True)]})
    recurring_donation_ids = fields.One2many(
        'donation.donation', 'source_recurring_id',
        string='Past Recurring Donations', readonly=True, copy=False)

    @api.constrains(
        'recurring_template', 'source_recurring_id', 'state',
        'tax_receipt_option')
    def _check_recurring_donation(self):
        for donation in self:
            if donation.recurring_template and donation.state != 'draft':
                raise ValidationError(_(
                    "The recurring donation template of '%s' must stay in "
                    "draft state.") % donation.partner_id.name)
            if donation.source_recurring_id and donation.recurring_template:
                raise ValidationError(_(
                    "The recurring donation template of '%s' cannot have "
                    "a Source Recurring Template")
                    % donation.partner_id.name)
            if (
                    donation.recurring_template and
                    donation.tax_receipt_option == 'each'):
                raise ValidationError(_(
                    "The recurring donation of %s cannot have a tax "
                    "receipt option 'Each'.")
                    % donation.partner_id.name)

    @api.depends('state', 'partner_id', 'move_id', 'recurring_template')
    def name_get(self):
        res = []
        for donation in self:
            if donation.state == 'draft':
                if donation.recurring_template == 'active':
                    name = _('Recurring Donation of %s') % (
                        donation.partner_id.name)
                elif donation.recurring_template == 'suspended':
                    name = _('Suspended Recurring Donation of %s') % (
                        donation.partner_id.name)
                else:
                    name = _('Draft Donation of %s') % donation.partner_id.name
            elif donation.state == 'cancel':
                name = _('Cancelled Donation of %s') % donation.partner_id.name
            else:
                name = donation.number
            res.append((donation.id, name))
        return res

    @api.onchange('recurring_template')
    def recurring_template_change(self):
        res = {'warning': {}}
        if self.recurring_template and self.tax_receipt_option == 'each':
            self.tax_receipt_option = 'annual'
            res['warning']['title'] = _('Update of Tax Receipt Option')
            res['warning']['message'] = _(
                "As it is a recurring donation, "
                "the Tax Receipt Option has been changed from Each to "
                "Annual. You may want to change it also on the Donor "
                "form.")
        if not self.recurring_template and self.partner_id:
            if self.partner_id.tax_receipt_option != self.tax_receipt_option:
                self.tax_receipt_option = self.partner_id.tax_receipt_option
        return res

    def unlink(self):
        for donation in self:
            # To avoid accidents !
            if donation.state == 'draft' and donation.recurring_template == 'active':
                raise UserError(_(
                    "You cannot delete an active recurring donation. "
                    "You must suspend it first."))
        return super(DonationDonation, self).unlink()
