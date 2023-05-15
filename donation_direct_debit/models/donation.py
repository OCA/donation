# Copyright 2015-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DonationDonation(models.Model):
    _inherit = "donation.donation"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Mandate",
        states={"done": [("readonly", True)]},
        tracking=True,
        check_company=True,
        ondelete="restrict",
        domain="[('state', '=', 'valid'), "
        "('partner_id', '=', commercial_partner_id), "
        "('company_id', '=', company_id)]",
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required", readonly=True
    )

    @api.onchange("payment_mode_id")
    def donation_partner_direct_debit_change(self):
        if (
            self.partner_id
            and self.payment_mode_id
            and self.payment_mode_id.payment_method_id.mandate_required
            and not self.mandate_id
        ):
            mandate = self.env["account.banking.mandate"].search(
                [
                    ("state", "=", "valid"),
                    ("partner_id", "=", self.commercial_partner_id.id),
                ],
                limit=1,
            )
            if mandate:
                self.mandate_id = mandate

    def _prepare_donation_move(self):
        vals = super()._prepare_donation_move()
        vals.update(
            {
                "mandate_id": self.mandate_id.id or False,
                "payment_mode_id": self.payment_mode_id.id,
            }
        )
        return vals

    def _prepare_payment_order(self):
        self.ensure_one()
        vals = {"payment_mode_id": self.payment_mode_id.id}
        return vals

    def validate(self):
        """Create Direct debit payment order on donation validation or update
        an existing draft Direct Debit pay order"""
        res = super().validate()
        apoo = self.env["account.payment.order"].sudo()
        for donation in self:
            if (
                donation.payment_mode_id
                and donation.payment_mode_id.payment_type == "inbound"
                and donation.payment_mode_id.payment_order_ok
                and donation.move_id
            ):
                payorders = apoo.search(
                    [
                        ("state", "=", "draft"),
                        ("company_id", "=", donation.company_id.id),
                        ("payment_mode_id", "=", donation.payment_mode_id.id),
                    ]
                )
                msg = False
                if payorders:
                    payorder = payorders[0]
                else:
                    payorder_vals = donation._prepare_payment_order()
                    payorder = apoo.create(payorder_vals)
                    msg = _(
                        "A new draft direct debit order "
                        "<a href=# data-oe-model=account.payment.order "
                        "data-oe-id=%d>%s</a> has been automatically created"
                    ) % (payorder.id, payorder.name)
                # add payment line
                payment_account_id = (
                    donation.payment_mode_id.fixed_journal_id.payment_debit_account_id.id
                )
                for mline in donation.move_id.line_ids:
                    if mline.account_id.id == payment_account_id:
                        mline.sudo().create_payment_line_from_move_line(payorder)
                        break
                if not msg:
                    msg = _(
                        "A new payment line has been automatically added "
                        "to the existing draft direct debit order "
                        "<a href=# data-oe-model=account.payment.order "
                        "data-oe-id=%d>%s</a>."
                    ) % (payorder.id, payorder.name)
                donation.message_post(body=msg)
        return res

    def done2cancel(self):
        for donation in self:
            if donation.move_id:
                donation_mv_line_ids = [line.id for line in donation.move_id.line_ids]
                if donation_mv_line_ids:
                    plines = self.env["account.payment.line"].search(
                        [
                            ("move_line_id", "in", donation_mv_line_ids),
                            ("company_id", "=", donation.company_id.id),
                            ("state", "in", ("draft", "open")),
                        ]
                    )
                    if plines:
                        raise UserError(
                            _(
                                "You cannot cancel a donation "
                                "which is linked to a payment line in a "
                                "direct debit order. Remove it from the "
                                "following direct debit order: %s."
                            )
                            % plines[0].order_id.display_name
                        )
        return super().done2cancel()
