# Copyright 2014-2016 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2016 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class DonationValidate(models.TransientModel):
    _name = "donation.validate"
    _description = "Validate Donations"

    def run(self):
        self.ensure_one()
        assert (
            self.env.context.get("active_model") == "donation.donation"
        ), "Source model must be donations"
        assert self.env.context.get("active_ids"), "No donations selected"
        donations = self.env["donation.donation"].browse(
            self.env.context.get("active_ids")
        )
        donations.filtered(lambda x: x.state == "draft").validate()
        return
