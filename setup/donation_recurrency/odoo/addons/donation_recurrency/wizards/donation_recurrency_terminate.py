# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DonationRecurrencyTerminate(models.TransientModel):

    _name = "donation.recurrency.terminate"
    _description = "Terminate Recurrency Wizard"

    contract_id = fields.Many2one(
        comodel_name="donation.recurrency",
        string="Contract",
        required=True,
        ondelete="cascade",
    )
    terminate_reason_id = fields.Many2one(
        comodel_name="donation.terminate.reason",
        string="Termination Reason",
        required=True,
        ondelete="cascade",
    )
    terminate_comment = fields.Text(string="Termination Comment")
    terminate_date = fields.Date(string="Termination Date", required=True)
    terminate_comment_required = fields.Boolean(
        related="terminate_reason_id.terminate_comment_required"
    )

    def terminate_contract(self):
        for wizard in self:
            wizard.contract_id._terminate_contract(
                wizard.terminate_reason_id,
                wizard.terminate_comment,
                wizard.terminate_date,
            )
        return True
