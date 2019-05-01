# © 2015-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    mandate_id = fields.Many2one(
        'account.banking.mandate',
        string='Mandate',
        ondelete='restrict',
        track_visibility='onchange',
        states={'done': [('readonly', True)]})  # domain is in the view

    payment_mode_id = fields.Many2one(
        'account.payment.mode',
        string="Payment Mode",
        readonly=True,
        ondelete='restrict',
        states={'draft': [('readonly', False)]},
        domain=[('payment_type', '=', 'inbound')])

    @api.onchange('partner_id')
    def donation_partner_direct_debit_change(self):
        if self.partner_id:
            self.payment_mode_id = self.partner_id.customer_payment_mode_id
            if (
                self.partner_id.customer_payment_mode_id.
                payment_method_id.mandate_required
            ):
                mandates = self.env['account.banking.mandate'].search([
                    ('state', '=', 'valid'),
                    ('partner_id', '=', self.commercial_partner_id.id),
                    ])
                if mandates:
                    self.mandate_id = mandates[0]
        else:
            self.payment_mode_id = False
            self.mandate_id = False

    def _prepare_counterpart_move_line(
            self, name, amount_total_company_cur, total_amount_currency,
            currency_id):
        vals = super(DonationDonation, self)._prepare_counterpart_move_line(
            name, amount_total_company_cur, total_amount_currency, currency_id)
        vals.update({
            'mandate_id': self.mandate_id.id or False,
            'payment_mode_id': self.payment_mode_id.id,
            })
        return vals

    def _prepare_payment_order(self):
        self.ensure_one()
        vals = {'payment_mode_id': self.payment_mode_id.id}
        return vals

    def validate(self):
        '''Create Direct debit payment order on donation validation or update
        an existing draft Direct Debit pay order'''
        res = super(DonationDonation, self).validate()
        apoo = self.env['account.payment.order']
        for donation in self:
            if (
                donation.payment_mode_id and
                donation.payment_mode_id.payment_type == 'inbound' and
                donation.payment_mode_id.payment_order_ok and
                donation.move_id
            ):
                payorders = apoo.search([
                    ('state', '=', 'draft'),
                    ('payment_mode_id', '=', donation.payment_mode_id.id),
                    ])
                msg = False
                if payorders:
                    payorder = payorders[0]
                else:
                    payorder_vals = donation._prepare_payment_order()
                    payorder = apoo.create(payorder_vals)
                    msg = _(
                        "A new draft direct debit order %s has been "
                        "automatically created") % payorder.name
                # add payment line
                bank_account = donation.journal_id.default_debit_account_id
                for mline in donation.move_id.line_ids:
                    if mline.account_id == bank_account:
                        mline.create_payment_line_from_move_line(payorder)
                if not msg:
                    msg = _("A new payment line has been automatically added "
                            "to the existing draft direct debit order "
                            "%s") % payorder.name
                donation.message_post(msg)
        return res

    def done2cancel(self):
        for donation in self:
            if donation.move_id:
                donation_mv_line_ids = [
                    l.id for l in donation.move_id.line_ids]
                if donation_mv_line_ids:
                    plines = self.env['account.payment.line'].search([
                        ('move_line_id', 'in', donation_mv_line_ids),
                        ('state', 'in', ('draft', 'open')),
                        ])
                    if plines:
                        raise UserError(_(
                            "You cannot cancel a donation "
                            "which is linked to a payment line in a "
                            "direct debit order. Remove it from the "
                            "following direct debit order: %s.")
                            % plines[0].order_id.name)
        return super(DonationDonation, self).done2cancel()
