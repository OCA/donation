# Copyright 2014-2016 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2016 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # begin with context_ to allow user to change it by himself
    context_donation_campaign_id = fields.Many2one(
        'donation.campaign',
        'Current Donation Campaign'
    )
    context_donation_journal_id = fields.Many2one(
        'account.journal',
        'Current Donation Payment Method',
        domain=[
            ('type', 'in', ('bank', 'cash')),
            ('allow_donation', '=', True)],
        company_dependent=True
    )
