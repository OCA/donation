# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp import models, fields


class DonationReport(models.Model):
    _name = "donation.report"
    _description = "Donations Analysis"
    _auto = False
    _rec_name = 'donation_date'
    _order = "donation_date desc"

    donation_date = fields.Date(string='Donation Date', readonly=True)
    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Donor', readonly=True)
    country_id = fields.Many2one(
        'res.country', string='Partner Country', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)
    product_categ_id = fields.Many2one(
        'product.category', string='Category of Product', readonly=True)
    campaign_id = fields.Many2one(
        'donation.campaign', string='Donation Campaign', readonly=True)
    in_kind = fields.Boolean(string='In Kind')
    amount_company_currency = fields.Float(
        'Amount Company Currency', readonly=True)

    def _select(self):
        select = """
            SELECT min(l.id) AS id,
                d.donation_date AS donation_date,
                l.product_id AS product_id,
                l.in_kind AS in_kind,
                pt.categ_id AS product_categ_id,
                d.company_id AS company_id,
                d.partner_id AS partner_id,
                d.country_id AS country_id,
                d.campaign_id AS campaign_id,
                sum(l.amount_company_currency) AS amount_company_currency
                """
        return select

    def _from(self):
        from_sql = """
            donation_line l
                LEFT JOIN donation_donation d ON (d.id=l.donation_id)
                LEFT JOIN product_product pp ON (l.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
            """
        return from_sql

    def _where(self):
        where = """
            WHERE d.state='done'
            """
        return where

    def _group_by(self):
        group_by = """
            GROUP BY l.product_id,
                l.in_kind,
                pt.categ_id,
                d.donation_date,
                d.partner_id,
                d.country_id,
                d.campaign_id,
                d.company_id
            """
        return group_by

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("CREATE OR REPLACE VIEW %s AS (%s FROM %s %s %s)" % (
            self._table, self._select(), self._from(),
            self._where(), self._group_by()))
