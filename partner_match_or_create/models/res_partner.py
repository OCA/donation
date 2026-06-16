# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _controller_try_match_partner(self, vals):
        email = vals["controller_email"]
        mobile = vals["controller_mobile"]
        partner_id = None
        if "res.partner.phone" in self.env:  # module base_partner_one2many_phone
            partner_phone = (
                self.env["res.partner.phone"]
                .sudo()
                .search_read(
                    [
                        ("type", "in", ("1_email_primary", "2_email_secondary")),
                        ("email", "=ilike", email),
                        ("partner_id", "!=", False),
                    ],
                    ["partner_id"],
                    limit=1,
                )
            )
            if partner_phone:
                partner_id = partner_phone[0]["partner_id"][0]
        else:
            partner = self.env["res.partner"].search_read(
                [("email", "=ilike", email)], ["id"], limit=1
            )
            if partner:
                partner_id = partner[0]["id"]
        if partner_id:
            logger.info("Match on email %s with partner ID %d", email, partner_id)
        # 'and vals['controller_country_id'] to make sure the mobile phone has been reformatted
        if not partner_id and mobile and vals["controller_country_id"]:
            if "res.partner.phone" in self.env:  # module base_partner_one2many_phone
                partner_phone = (
                    self.env["res.partner.phone"]
                    .sudo()
                    .search_read(
                        [
                            ("type", "in", ("5_mobile_primary", "6_mobile_secondary")),
                            ("phone", "=", mobile),
                            ("partner_id", "!=", False),
                        ],
                        ["partner_id"],
                        limit=1,
                    )
                )
                if partner_phone:
                    partner_id = partner_phone[0]["partner_id"][0]
            else:
                partner = self.env["res.partner"].search_read(
                    [("mobile", "=", mobile)], ["id"], limit=1
                )
                if partner:
                    partner_id = partner[0]["id"]
            if partner_id:
                logger.info("Match on mobile %s with partner ID %d", mobile, partner_id)
        if not partner_id:
            logger.info("No match on an existing partner")
        return partner_id
