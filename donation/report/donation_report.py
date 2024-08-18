# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import sql

from odoo import fields, models, tools


class DonationReport(models.Model):
    _name = "donation.report"
    _description = "Donations Analysis"
    _auto = False
    _rec_name = "donation_date"
    _order = "donation_date desc"

    donation_date = fields.Date(readonly=True)
    product_id = fields.Many2one("product.product", readonly=True)
    product_detailed_type = fields.Selection(
        related="product_id.detailed_type", store=True
    )
    partner_id = fields.Many2one("res.partner", "Donor", readonly=True)
    country_id = fields.Many2one("res.country", "Partner Country", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    product_categ_id = fields.Many2one(
        "product.category", "Category of Product", readonly=True
    )
    campaign_id = fields.Many2one(
        "donation.campaign", "Donation Campaign", readonly=True
    )
    payment_mode_id = fields.Many2one("account.payment.mode", readonly=True)
    thanks_printed = fields.Boolean(readonly=True)
    thanks_template_id = fields.Many2one(
        "donation.thanks.template", string="Thanks Template", readonly=True
    )
    in_kind = fields.Boolean()
    tax_receipt_ok = fields.Boolean("Eligible for a Tax Receipt")
    company_currency_id = fields.Many2one("res.currency", readonly=True)
    amount_company_currency = fields.Monetary(
        "Amount", readonly=True, currency_field="company_currency_id"
    )
    tax_receipt_amount = fields.Monetary(
        "Tax Receipt Eligible Amount",
        readonly=True,
        currency_field="company_currency_id",
    )

    def _select(self):
        return sql.SQL(
            """
            SELECT min(l.id) AS id,
                d.donation_date,
                l.product_id,
                l.product_detailed_type,
                l.in_kind,
                l.tax_receipt_ok,
                pt.categ_id AS product_categ_id,
                d.company_id,
                d.payment_mode_id,
                d.partner_id,
                d.country_id,
                d.campaign_id,
                d.company_currency_id,
                d.thanks_printed,
                d.thanks_template_id,
                sum(l.amount_company_currency) AS amount_company_currency,
                sum(l.tax_receipt_amount) AS tax_receipt_amount
                """
        )

    def _from(self):
        return sql.SQL(
            """
            donation_line l
                LEFT JOIN donation_donation d ON (d.id=l.donation_id)
                LEFT JOIN product_product pp ON (l.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
            """
        )

    def _where(self):
        return sql.SQL(
            """
            WHERE d.state='done'
            """
        )

    def _group_by(self):
        return sql.SQL(
            """
            GROUP BY l.product_id,
                l.product_detailed_type,
                l.in_kind,
                l.tax_receipt_ok,
                pt.categ_id,
                d.donation_date,
                d.partner_id,
                d.country_id,
                d.campaign_id,
                d.company_id,
                d.payment_mode_id,
                d.thanks_printed,
                d.thanks_template_id,
                d.company_currency_id
            """
        )

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = sql.SQL("CREATE OR REPLACE VIEW {0} AS ({1} FROM {2} {3} {4})").format(
            sql.Identifier(self._table),
            self._select(),
            self._from(),
            self._where(),
            self._group_by(),
        )  # pylint: disable=sql-injection
        self._cr.execute(query)
