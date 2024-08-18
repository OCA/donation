# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

logger = logging.getLogger(__name__)


class TaxReceiptAnnualCreate(models.TransientModel):
    _name = "tax.receipt.annual.create"
    _description = "Generate Annual Tax Receipts"

    @api.model
    def _default_end_date(self):
        return datetime.date(fields.Date.context_today(self).year - 1, 12, 31)

    @api.model
    def _default_start_date(self):
        return datetime.date(fields.Date.context_today(self).year - 1, 1, 1)

    start_date = fields.Date(
        required=True, default=lambda self: self._default_start_date()
    )
    end_date = fields.Date(required=True, default=lambda self: self._default_end_date())
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.model
    def _prepare_annual_tax_receipt(self, partner, partner_dict):
        vals = {
            "company_id": self.company_id.id,
            "currency_id": self.company_id.currency_id.id,
            "amount": partner_dict["amount"],
            "type": "annual",
            "partner_id": partner.id,
            "date": self.end_date,
            "donation_date": self.end_date,
        }
        # designed to add add O2M fields donation_ids and invoice_ids
        vals.update(partner_dict["extra_vals"])
        return vals

    def generate_annual_receipts(self):
        self.ensure_one()
        logger.info(
            "Start to generate annual fiscal receipts from %s to %s",
            self.start_date,
            self.end_date,
        )
        dtro = self.env["donation.tax.receipt"]
        tax_receipt_annual_dict = {}
        self.env["donation.tax.receipt"].update_tax_receipt_annual_dict(
            tax_receipt_annual_dict, self.start_date, self.end_date, self.company_id
        )
        tax_receipt_ids = []
        existing_annual_receipts = dtro.search(
            [
                ("donation_date", "<=", self.end_date),
                ("donation_date", ">=", self.start_date),
                ("company_id", "=", self.company_id.id),
                ("type", "=", "annual"),
            ]
        )
        existing_annual_receipts_dict = {}
        for receipt in existing_annual_receipts:
            existing_annual_receipts_dict[receipt.partner_id] = receipt

        for partner, partner_dict in tax_receipt_annual_dict.items():
            # Block if the partner already has an annual tax receipt
            if partner in existing_annual_receipts_dict:
                existing_receipt = existing_annual_receipts_dict[partner]
                raise UserError(
                    _(
                        "The Donor '%(partner)s' already has an annual tax receipt "
                        "in this timeframe: %(receipt)s dated %(number)s.",
                        partner=partner.display_name,
                        receipt=existing_receipt.number,
                        date=format_date(self.env, existing_receipt.date),
                    )
                )
            vals = self._prepare_annual_tax_receipt(partner, partner_dict)
            tax_receipt = dtro.create(vals)
            tax_receipt_ids.append(tax_receipt.id)
            logger.info("Tax receipt %s generated", tax_receipt.number)
        if not tax_receipt_ids:
            raise UserError(_("No annual tax receipt to generate"))
        logger.info("%d annual fiscal receipts generated", len(tax_receipt_ids))
        action = (
            self.env.ref("donation_base.donation_tax_receipt_action").sudo().read([])[0]
        )
        action["domain"] = [("id", "in", tax_receipt_ids)]
        return action
