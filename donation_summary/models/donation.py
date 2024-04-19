from odoo import fields, models


class Donation(models.Model):
    _inherit = "donation.donation"

    donation_summary_id = fields.Many2one(
        string="Donation Summary", comodel_name="donation.summary"
    )
