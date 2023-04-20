# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """UPDATE product_template
        SET detailed_type='donation_in_kind_service'
        WHERE donation IS true AND in_kind_donation IS true AND type = 'service'"""
    )
    cr.execute(
        """UPDATE product_template
        SET detailed_type='donation_in_kind_consu'
        WHERE donation IS true AND in_kind_donation IS true AND type = 'consu'"""
    )
    cr.execute(
        """UPDATE product_template
        SET detailed_type='donation'
        WHERE donation IS true AND in_kind_donation IS NOT true"""
    )
