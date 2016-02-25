# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Direct Debit module for Odoo
#    Copyright (C) 2015 Akretion (www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Mandate',
        states={'done': [('readonly', True)]}, track_visibility='onchange',
        ondelete='restrict')

    @api.model
    def _prepare_payment_order(self, payment_mode):
        vals = {
            'mode': payment_mode.id,
            'payment_order_type': 'debit',
            }
        return vals

    @api.model
    def _prepare_payment_line(self, donation, payment_order):
        abmo = self.env['account.banking.mandate']
        move_line = False
        for aml in donation.move_id.line_id:
            if aml.account_id == donation.journal_id.default_credit_account_id:
                move_line = aml
                break
        assert move_line, 'Could not match the payment move line'

        if not donation.mandate_id:
            mandates = abmo.search([
                ('partner_id', '=', donation.partner_id.id),
                ('state', '=', 'valid'),
                ])
            if not mandates:
                raise Warning(
                    _('No valid mandate found for donor %s')
                    % donation.partner_id.name)
            mandate = mandates[0]
        else:
            mandate = donation.mandate_id
        vals = {
            'order_id': payment_order.id,
            'move_line_id': move_line.id,
            'partner_id': move_line.partner_id.id,
            'amount_currency': move_line.debit,
            'communication':
            donation.payment_ref or donation.number.replace('/', '-'),
            'state': 'normal',
            'date': move_line.date_maturity,  # TODO Not set ?
            'currency': donation.currency_id.id,
            'mandate_id': mandate.id,
            'bank_id': mandate.partner_bank_id.id,
            }
        return vals

    @api.one
    def validate(self):
        '''Create Direct debit payment order on donation validation or update
        an existing draft Direct Debit pay order'''
        res = super(DonationDonation, self).validate()
        paymodes = self.env['payment.mode'].search([
            ('journal', '=', self.journal_id.id),
            ('payment_order_type', '=', 'debit'),
            ('company_id', '=', self.company_id.id),
            ('type.code', '=like', 'pain.008.001.%')])
        if len(paymodes) > 1:
            raise Warning(
                _("There are 2 payment modes with the same bank journal!"))
        if paymodes and self.move_id:
            paymode = paymodes[0]
            poo = self.env['payment.order']
            payorders = poo.search([
                ('state', '=', 'draft'),
                ('payment_order_type', '=', 'debit'),
                ('mode', '=', paymode.id),
                # mode is attached to company
                ])
            msg = False
            if payorders:
                payorder = payorders[0]
            else:
                payorder_vals = self._prepare_payment_order(paymode)
                payorder = poo.create(payorder_vals)
                msg = _(
                    "A new draft direct debit order %s has been "
                    "automatically created") % payorder.reference
            # add payment line
            payline_vals = self._prepare_payment_line(self, payorder)
            self.env['payment.line'].create(payline_vals)
            if not msg:
                msg = _("A new payment line has been automatically added "
                        "to the existing draft direct debit order "
                        "%s") % payorder.reference
            self.message_post(msg)
        return res

    @api.one
    def done2cancel(self):
        if self.move_id:
            donation_mv_line_ids = [l.id for l in self.move_id.line_id]
            if donation_mv_line_ids:
                plines = self.env['payment.line'].search([
                    ('move_line_id', 'in', donation_mv_line_ids),
                    ('order_id.state', 'in', ('draft', 'open')),
                    ])
                if plines:
                    raise Warning(
                        _("You cannot cancel a donation "
                            "which is linked to a payment line in a "
                            "direct debit order. Remove it from the "
                            "following direct debit order: %s.")
                        % plines[0].order_id.reference)
        return super(DonationDonation, self).done2cancel()
