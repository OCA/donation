# Copyright 2016-2021 La Cimade (http://www.lacimade.org/)
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tax_receipt_option = fields.Selection(
        [('none', 'None'),
         ('each', 'For Each Donation'),
         ('annual', 'Annual Tax Receipt')],
        string='Tax Receipt Option',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company Currency',
        readonly=True
    )
    tax_receipt_total = fields.Monetary(
        compute='_compute_tax_receipt_total',
        string='Eligible Tax Receipt Sub-total',
        store=True,
        currency_field='company_currency_id',
    )

    @api.depends(
        'pricelist_id.currency_id', 'order_line.product_id', 'order_line.price_subtotal')
    def _compute_tax_receipt_total(self):
        for sale in self:
            total = 0.0
            for line in sale.order_line:
                if line.product_id and line.product_id.tax_receipt_ok:
                    # there are not sale taxes on tax receipts
                    total += line.product_uom_qty * line.price_unit *\
                        (1 - (line.discount or 0.0) / 100.0)
            total_cc = sale.currency_id._convert(
                total, sale.company_id.currency_id, sale.company_id, sale.date_order or fields.Date.context_today(self))
            sale.tax_receipt_total = total_cc

    @api.onchange('partner_id')
    def donation_sale_change(self):
        if self.partner_id:
            self.tax_receipt_option = self.partner_id.commercial_partner_id.tax_receipt_option
        else:
            self.tax_receipt_option = False

    @api.onchange('tax_receipt_option')
    def tax_receipt_option_change(self):
        res = {}
        if (
                self.partner_id and
                self.partner_id.commercial_partner_id.tax_receipt_option == 'annual' and
                self.tax_receipt_option != 'annual'):
            res = {
                'warning': {
                    'title': _('Error:'),
                    'message':
                    _('You cannot change the Tax Receipt '
                        'Option when it is Annual.'),
                    },
                }
            self.tax_receipt_option = 'annual'
        return res

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals['tax_receipt_option'] = self.tax_receipt_option
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tax_receipt_ok = fields.Boolean(
        related='product_id.tax_receipt_ok',
        store=True,
    )
    # We don't handle in_kind donations via donation_sale for the moment
    # in_kind = fields.Boolean(
    #    related='product_id.in_kind_donation', readonly=True, store=True,
    #    string='In Kind')

    @api.constrains('product_id', 'tax_id')
    def donation_sale_line_check(self):
        for line in self:
            if line.product_id and line.product_id.tax_receipt_ok and line.tax_id:
                raise ValidationError(_(
                    "On the sale order '%s', the sale order line '%s' "
                    "has a donation product, so it should not have taxes.")
                    % (line.order_id.name, line.name))
