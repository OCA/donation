# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    allow_donation = fields.Boolean(string='Donation Payment Method')

    @api.multi
    @api.constrains('type', 'allow_donation')
    def _check_donation(self):
        for journal in self:
            if journal.allow_donation and journal.type not in ('bank', 'cash'):
                raise ValidationError(_(
                    "The journal '%s' has the option "
                    "'Donation Payment Method', so it's type should "
                    "be 'Cash' or 'Bank and Checks'.") % journal.name)

    @api.onchange('type')
    def donation_journal_type_change(self):
        if self.type in ('cash', 'bank'):
            self.allow_donation = True
