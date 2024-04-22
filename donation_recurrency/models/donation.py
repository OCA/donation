from odoo import _, api, fields, models


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    contract_id = fields.Many2one(
        "donation.recurrency", string="Recurrency reference", index=True
    )
