from odoo import models


class TaxReceiptAnnualCreate(models.TransientModel):
    _inherit = "tax.receipt.annual.create"
    """
    Clase creada para cuando se me pida cambiar la vista o funcionamiento de
    'Crear recibos anuales', de momento no hace nada.
    """

    # @api.model
    # def _prepare_annual_tax_receipt(self, partner, partner_dict):
    #     # wdb.set_trace()
    #     super()._prepare_annual_tax_receipt(partner, partner_dict)

    # def generate_annual_receipts(self):
    #     # wdb.set_trace()
    #     super().generate_annual_receipts()
