from odoo import api, fields, models


class Move(models.Model):
    _inherit = 'stock.move'

    donation_line_id = fields.Many2one(comodel_name='donation.line')
    created_donation_line_id = fields.Many2one(comodel_name='donation.line')
