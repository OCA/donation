# Copyright 2025 Akretion France (https://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Match or Create",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "summary": "Create a new partner or match an existing partner",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/donation",
    "depends": ["phone_validation"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_title.xml",
        "wizards/partner_match_or_create.xml",
    ],
    "post_init_hook": "res_partner_title_postinstall",
    "installable": True,
}
