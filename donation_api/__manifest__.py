# Copyright 2025 Akretion France (https://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Donation",
    "version": "14.0.1.0.0",
    "category": "Donation",
    "license": "AGPL-3",
    "summary": "API for donation module",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": ["donation", "fastapi", "partner_match_or_create"],
    "external_dependencies": {"python": ["fastapi", "pydantic<2"]},
    "data": [
        "data/res_users.xml",
        #        "security/ir.model.access.csv",
        "wizards/res_config_settings_view.xml",
        "views/donation_donation.xml",
        #        "data/mail_template.xml",
    ],
    "installable": True,
}
