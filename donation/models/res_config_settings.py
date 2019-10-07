# -*- coding: utf-8 -*-
# 2019 initOS GmbH (Amjad Enaya <amjad.enaya@initos.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_donation_sale = fields.Boolean('Donation Sale')
    module_donation_bank_statement = fields.Boolean('Donation Bank Statement')
    module_donation_direct_debit = fields.Boolean('Donation Direct Debit')
    module_donation_recurring = fields.Boolean('Donation Recurring')




