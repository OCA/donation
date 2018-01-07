# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class DonationLine(models.Model):
    _inherit = 'donation.line'

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(DonationLine, self).product_id_change()
        if self.product_id:
            ana_accounts = self.product_id.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts['income']
            print "ana_account=", ana_account
            self.analytic_account_id = ana_account.id
        return res

    @api.model
    def create(self, vals):
        if vals.get('product_id') and not vals.get('analytic_account_id'):
            product = self.env['product.product'].browse(
                vals.get('product_id'))
            ana_accounts = product.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts['income']
            vals['analytic_account_id'] = ana_account.id
        return super(DonationLine, self).create(vals)
