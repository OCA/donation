# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Donation Portal",
    "summary": "Donation overview on the portal",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/donation",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "maintainers": ["mihien"],
    "license": "AGPL-3",
    "depends": [
        "donation",
        "portal",
    ],
    "data": [
        "security/donation_portal_security.xml",
        "security/ir.model.access.csv",
        "views/donation_portal_templates.xml",
    ],
    "installable": True,
}
