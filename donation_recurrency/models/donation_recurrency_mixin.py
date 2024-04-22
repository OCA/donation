# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
# from odoo import api, fields, models


class DonationRecurrencyBasicMixin(models.AbstractModel):
    _name = "donation.recurrency.basic.mixin"
    _description = "Basic recurrency mixin for abstract donation models"

    recurring_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Recurrence",
        help="Specify Interval for automatic donation generation.",
    )
    recurring_donation_type = fields.Selection(
        [("pre-paid", "Pre-paid"), ("post-paid", "Post-paid")],
        default="pre-paid",
        string="Donation type",
        help=(
            "Specify if the donation must be generated at the beginning "
            "(pre-paid) or end (post-paid) of the period."
        ),
    )
    recurring_donation_offset = fields.Integer(
        compute="_compute_recurring_donation_offset",
        string="Donation offset",
        help=(
            "Number of days to offset the donation from the period end "
            "date (in post-paid mode) or start date (in pre-paid mode)."
        ),
    )
    recurring_interval = fields.Integer(
        default=1,
        string="Donation Every",
        help="Donation every (Days/Week/Month/Year)",
    )
    date_start = fields.Date()
    recurring_next_date = fields.Date(string="Date of Next Donation", readonly=True)

    @api.depends("recurring_donation_type", "recurring_rule_type")
    def _compute_recurring_donation_offset(self):
        for rec in self:
            method = self._get_default_recurring_donation_offset
            rec.recurring_donation_offset = method(
                rec.recurring_donation_type, rec.recurring_rule_type
            )

    @api.model
    def _get_default_recurring_donation_offset(
        self, recurring_donation_type, recurring_rule_type
    ):
        if (
            recurring_donation_type == "pre-paid"
            or recurring_rule_type == "monthlylastday"
        ):
            return 0
        else:
            return 1


class DonationRecurrencyMixin(models.AbstractModel):
    _inherit = "donation.recurrency.basic.mixin"
    _name = "donation.recurrency.mixin"
    _description = "Recurrency mixin for donation models"

    date_start = fields.Date(default=lambda self: fields.Date.context_today(self))
    recurring_next_date = fields.Date(
        compute="_compute_recurring_next_date", store=True, readonly=False, copy=True
    )
    date_end = fields.Date(index=True)
    next_period_date_start = fields.Date(
        string="Next Period Start",
        compute="_compute_next_period_date_start",
    )
    next_period_date_end = fields.Date(
        string="Next Period End",
        compute="_compute_next_period_date_end",
    )
    # termination_notice_date = fields.Date(
    #     compute="_compute_termination_notice_date",
    #     store=True,
    #     copy=False,
    # )
    last_date_donated = fields.Date(readonly=True, copy=False)
    manual_renew_needed = fields.Boolean(
        default=False,
        help="This flag is used to make a difference between a definitive stop"
        "and temporary one for which a user is not able to plan a"
        "successor in advance",
    )

    @api.depends("next_period_date_start")
    def _compute_recurring_next_date(self):
        for rec in self:
            rec.recurring_next_date = self.get_next_donation_date(
                rec.next_period_date_start,
                rec.recurring_donation_type,
                rec.recurring_donation_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
            )

    @api.depends("last_date_donated", "date_start", "date_end")
    def _compute_next_period_date_start(self):
        for rec in self:
            if rec.last_date_donated:
                next_period_date_start = rec.last_date_donated + relativedelta(days=1)
            else:
                next_period_date_start = rec.date_start
            if (
                rec.date_end
                and next_period_date_start
                and next_period_date_start > rec.date_end
            ):
                next_period_date_start = False
            rec.next_period_date_start = next_period_date_start

    @api.depends(
        "next_period_date_start",
        "recurring_donation_type",
        "recurring_donation_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "recurring_next_date",
    )
    def _compute_next_period_date_end(self):
        for rec in self:
            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_donation_date=rec.recurring_next_date,
                recurring_donation_type=rec.recurring_donation_type,
                recurring_donation_offset=rec.recurring_donation_offset,
            )

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        """Return a relativedelta for one period.

        When added to the first day of the period,
        it gives the first day of the next period.
        """
        if recurring_rule_type == "daily":
            return relativedelta(days=interval)
        elif recurring_rule_type == "weekly":
            return relativedelta(weeks=interval)
        elif recurring_rule_type == "monthly":
            return relativedelta(months=interval)
        elif recurring_rule_type == "monthlylastday":
            return relativedelta(months=interval, day=1)
        elif recurring_rule_type == "quarterly":
            return relativedelta(months=3 * interval)
        elif recurring_rule_type == "semesterly":
            return relativedelta(months=6 * interval)
        else:
            return relativedelta(years=interval)

    @api.model
    def get_next_period_date_end(
        self,
        next_period_date_start,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        next_donation_date=False,
        recurring_donation_type=False,
        recurring_donation_offset=False,
    ):
        """Compute the end date for the next period.

        The next period normally depends on recurrence options only.
        It is however possible to provide it a next donation date, in
        which case this method can adjust the next period based on that
        too. In that scenario it required the donation type and offset
        arguments.
        """
        if not next_period_date_start:
            return False
        if max_date_end and next_period_date_start > max_date_end:
            # start is past max date end: there is no next period
            return False
        if not next_donation_date:
            # regular algorithm
            next_period_date_end = (
                next_period_date_start
                + self.get_relative_delta(recurring_rule_type, recurring_interval)
                - relativedelta(days=1)
            )
        else:
            # special algorithm when the next donation date is forced
            if recurring_donation_type == "pre-paid":
                next_period_date_end = (
                    next_donation_date
                    - relativedelta(days=recurring_donation_offset)
                    + self.get_relative_delta(recurring_rule_type, recurring_interval)
                    - relativedelta(days=1)
                )
            else:  # post-paid
                next_period_date_end = next_donation_date - relativedelta(
                    days=recurring_donation_offset
                )
        if max_date_end and next_period_date_end > max_date_end:
            # end date is past max_date_end: trim it
            next_period_date_end = max_date_end
        return next_period_date_end

    @api.model
    def get_next_donation_date(
        self,
        next_period_date_start,
        recurring_donation_type,
        recurring_donation_offset,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
    ):
        next_period_date_end = self.get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end=max_date_end,
        )
        if not next_period_date_end:
            return False
        if recurring_donation_type == "pre-paid":
            recurring_next_date = next_period_date_start + relativedelta(
                days=recurring_donation_offset
            )
        else:  # post-paid
            recurring_next_date = next_period_date_end + relativedelta(
                days=recurring_donation_offset
            )
        return recurring_next_date
