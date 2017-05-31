# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    donation = fields.Boolean(
        string='Is a Donation', track_visibility='onchange')
    in_kind_donation = fields.Boolean(
        string="In-Kind Donation", track_visibility='onchange')
    tax_receipt_ok = fields.Boolean(
        string='Is Eligible for a Tax Receipt', track_visibility='onchange',
        help="Specify if the product is eligible for a tax receipt")

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'
            self.taxes_id = False
            self.supplier_taxes_id = False

    @api.onchange('in_kind_donation')
    def _in_kind_donation_change(self):
        if self.in_kind_donation:
            self.donation = True

    @api.multi
    @api.constrains('donation', 'type')
    def donation_check(self):
        for product in self:
            if product.donation and product.type != 'service':
                raise ValidationError(_(
                    "The product '%s' is a donation, so you must "
                    "configure it as a Service") % product.name)
            if product.in_kind_donation and not product.donation:
                raise ValidationError(_(
                    "The option 'In-Kind Donation' is active on "
                    "the product '%s', so you must also activate the "
                    "option 'Is a Donation'.") % product.name)
            if product.tax_receipt_ok and not product.donation:
                raise ValidationError(_(
                    "The option 'Is Eligible for a Tax Receipt' is "
                    "active on the product '%s', so you must also activate "
                    "the option 'Is a Donation'.") % product.name)
            # The check below is to make sure that we don't forget to remove
            # the default sale VAT tax on the donation product, particularly
            # for users of donation_sale. If there are countries that have
            # sale tax on donations (!), please tell us and we can remove this
            # constraint
            if product.donation and product.taxes_id:
                raise ValidationError(_(
                    "There shouldn't have any Customer Taxes on the "
                    "donation product '%s'.") % product.name)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('donation')
    def _donation_change(self):
        if self.donation:
            self.type = 'service'

    @api.onchange('in_kind_donation')
    def _in_kind_donation_change(self):
        if self.in_kind_donation:
            self.donation = True
