# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def donation_action_reset_domain(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    donation_module = env["ir.module.module"].search(
        [("name", "=", "donation")], limit=1
    )
    if donation_module and donation_module.state == "installed":
        env.ref("donation.donation_action").write({"domain": False})
        logger.info("Donation action reseted to empty domain")
