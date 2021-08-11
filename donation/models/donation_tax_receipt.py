# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DonationTaxReceipt(models.Model):
    _inherit = "donation.tax.receipt"

    donation_ids = fields.One2many(
        "donation.donation", "tax_receipt_id", string="Related Donations"
    )

    @api.model
    def update_tax_receipt_annual_dict(
        self, tax_receipt_annual_dict, start_date, end_date, company
    ):
        super().update_tax_receipt_annual_dict(
            tax_receipt_annual_dict, start_date, end_date, company
        )
        donations = self.env["donation.donation"].search(
            [
                ("donation_date", ">=", start_date),
                ("donation_date", "<=", end_date),
                ("tax_receipt_option", "=", "annual"),
                ("tax_receipt_id", "=", False),
                ("tax_receipt_total", "!=", 0),
                ("company_id", "=", company.id),
                ("state", "=", "done"),
            ]
        )
        for donation in donations:
            # tax_receipt_total is in company currency
            tax_receipt_amount = donation.tax_receipt_total
            if company.currency_id.is_zero(tax_receipt_amount):
                continue
            partner = donation.commercial_partner_id
            if partner not in tax_receipt_annual_dict:
                tax_receipt_annual_dict[partner] = {
                    "amount": tax_receipt_amount,
                    "extra_vals": {"donation_ids": [(6, 0, [donation.id])]},
                }
            else:
                tax_receipt_annual_dict[partner]["amount"] += tax_receipt_amount
                tax_receipt_annual_dict[partner]["extra_vals"]["donation_ids"][0][
                    2
                ].append(donation.id)
