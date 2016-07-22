# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    donation_credit_transfer_journal_id = fields.Many2one(
        'account.journal', string='Journal for Donations via Credit Transfer')
    donation_credit_transfer_product_id = fields.Many2one(
        'product.product', string='Product for Donations via Credit Transfer',
        domain=[('donation', '=', True)], ondelete='restrict')

    @api.multi
    @api.constrains('donation_credit_transfer_product_id')
    def company_donation_bank_statement_check(self):
        for company in self:
            product = company.donation_credit_transfer_product_id
            if product and not product.donation:
                raise ValidationError(_(
                    "On the company %s, the Product for Donations "
                    "via Credit Transfer (%s) is not a donation product !")
                    % (company.name, product.name))
