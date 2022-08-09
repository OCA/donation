# Copyright 2022 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Donation Pos",
    "summary": """
        This addon connects modules donation to POS.""",
    "version": "12.0.0.0.1",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/donation",
    "depends": [
        "donation_base",
        "point_of_sale",
    ],
    "data": [
        "views/templates.xml",
        "views/view_pos_order.xml",
        "views/pos_config_view.xml",
    ],
    "demo": [],
    "qweb": [
        "static/src/xml/donation_pos.xml",
    ],
}
