# from datetime import timedelta

# from dateutil.relativedelta import relativedelta

from odoo import fields, models
# from odoo.exceptions import ValidationError

# from .contract_line_constraints import get_allowed


class DonationLine(models.Model):
    _name = "donation.line"
    _description = "Donation Line"
    _inherit = [
        # "donation.abstract.recurrency.line",
        "donation.recurrency.mixin",
        # "analytic.mixin",
    ]
    _order = "sequence,id"

    sequence = fields.Integer()
    donation_id = fields.Many2one(
        comodel_name="donation.recurrency",
        string="Donation",
        required=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
    )
    state = fields.Selection(
        selection=[
            ("upcoming", "Upcoming"),
            ("in-progress", "In-progress"),
            ("to-renew", "To renew"),
            ("upcoming-close", "Upcoming Close"),
            ("closed", "Closed"),
            ("canceled", "Canceled"),
        ],
        compute="_compute_state",
        search="_search_state",
    )
    currency_id = fields.Many2one(related="donation_id.currency_id")
    date_start = fields.Date(required=True)
    # date_end = fields.Date(compute="_compute_date_end", store=True, readonly=False)

    # @api.depends("donation_id.date_end", "donation_id.line_recurrence")
    # def _compute_date_end(self):
    #     self._set_recurrence_field("date_end")
