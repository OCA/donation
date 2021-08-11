# Copyright 2017 Barroux Abbey (www.barroux.org)
# Copyright 2017 Akretion France (www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>

from odoo import fields, models


class DonationTaxReceiptOptionSwitch(models.TransientModel):
    _name = "donation.tax.receipt.option.switch"
    _description = "Switch Donation Tax Receipt Option"

    donation_id = fields.Many2one(
        "donation.donation",
        string="Donation",
        required=True,
        default=lambda self: self._context.get("active_id"),
    )
    new_tax_receipt_option = fields.Selection(
        [("each", "For Each Donation"), ("annual", "Annual Tax Receipt")],
        string="Tax Receipt Option",
        required=True,
    )

    def switch(self):
        self.ensure_one()
        assert self.donation_id, "Missing donation"
        assert not self.donation_id.tax_receipt_id, "Already linked to a tax receipt"
        self.donation_id.write({"tax_receipt_option": self.new_tax_receipt_option})
        receipt = self.donation_id.generate_each_tax_receipt()
        if receipt:
            self.donation_id.write({"tax_receipt_id": receipt.id})
        return
