# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import get_lang
import wdb


class DonationTaxReceiptPrint(models.TransientModel):
    _inherit = "donation.tax.receipt.print"
    _description = "Print Donation Tax Receipts"

    lang = fields.Selection(
        [("es_ES", "Spanish"), ("ca_ES", "Catalan"), ("fr_FR", "French"), ("en_GB", "English")],
        # readonly=True,
        # copy=False,
        # default="draft",
        # index=True,
        # tracking=True,
    )

    def print_receipts(self):
        self.ensure_one()
        if not self.receipt_ids:
            raise UserError(_("There are no tax receipts to print."))
        today = fields.Date.context_today(self)
        self.receipt_ids.write({"print_date": today})
        if self.lang:
            lang = self.lang
        else:
            lang = get_lang(self.env).code
        report_action_py3o = self.get_ref_report_name(lang)
        return self.env.ref(report_action_py3o).report_action(self.receipt_ids)

    def get_ref_report_name(self, lang):
        report_names = {
            'es_ES': "donation_certificate.donation_certificate_report_py3o_ES",
            'ca_ES': "donation_certificate.donation_certificate_report_py3o_CAT",
            'fr_FR': "donation_certificate.donation_certificate_report_py3o_FR",
            'en_GB': "donation_certificate.donation_certificate_report_py3o_EN"
        }

        return report_names.get(lang, "donation_certificate.donation_certificate_report_py3o_EN")
