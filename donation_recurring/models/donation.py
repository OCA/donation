# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DonationDonation(models.Model):
    _inherit = "donation.donation"

    recurring_template = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended")],
        copy=False,
        index=True,
        tracking=True,
    )
    source_recurring_id = fields.Many2one(
        "donation.donation",
        string="Source Recurring Template",
        states={"done": [("readonly", True)]},
    )
    recurring_donation_ids = fields.One2many(
        "donation.donation",
        "source_recurring_id",
        string="Past Recurring Donations",
        readonly=True,
        copy=False,
    )

    @api.constrains(
        "recurring_template", "source_recurring_id", "state", "tax_receipt_option"
    )
    def _check_recurring_donation(self):
        for donation in self:
            if donation.recurring_template and donation.state != "draft":
                raise ValidationError(
                    _("The recurring donation template %s must stay in draft state.")
                    % donation.number
                )
            if donation.source_recurring_id and donation.recurring_template:
                raise ValidationError(
                    _(
                        "The recurring donation template %s cannot have "
                        "a Source Recurring Template"
                    )
                    % donation.number
                )
            if donation.recurring_template and donation.tax_receipt_option == "each":
                raise ValidationError(
                    _(
                        "The recurring donation %s cannot have a tax "
                        "receipt option 'Each'."
                    )
                    % donation.number
                )

    @api.depends("state", "partner_id", "move_id", "recurring_template")
    def name_get(self):
        res = []
        for donation in self:
            if donation.recurring_template == "active":
                name = _("Recurring Donation %s") % (donation.number)
            elif donation.recurring_template == "suspended":
                name = _("Suspended Recurring Donation %s") % (donation.number)
            else:
                name = super(DonationDonation, donation).name_get()[0][1]
            res.append((donation.id, name))
        return res

    @api.onchange("recurring_template")
    def recurring_template_change(self):
        res = {"warning": {}}
        if self.recurring_template and self.tax_receipt_option == "each":
            self.tax_receipt_option = "annual"
            res["warning"]["title"] = _("Update of Tax Receipt Option")
            res["warning"]["message"] = _(
                "As it is a recurring donation, "
                "the Tax Receipt Option has been changed from Each to "
                "Annual. You may want to change it also on the Donor form."
            )
        if not self.recurring_template and self.commercial_partner_id:
            if self.commercial_partner_id.tax_receipt_option != self.tax_receipt_option:
                self.tax_receipt_option = self.commercial_partner_id.tax_receipt_option
        return res

    def active2suspended(self):
        self.ensure_one()
        assert self.recurring_template == "active"
        self.write({"recurring_template": "suspended"})

    def suspended2active(self):
        self.ensure_one()
        assert self.recurring_template == "suspended"
        self.write({"recurring_template": "active"})

    def unlink(self):
        for donation in self:
            # To avoid accidents !
            if donation.recurring_template == "active":
                raise UserError(
                    _(
                        "You cannot delete an active recurring donation. "
                        "You must suspend it first."
                    )
                )
        return super().unlink()
