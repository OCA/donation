# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
)
from odoo.addons.portal.controllers.portal import (
    pager as portal_pager,
)


class DonationCustomerPortal(CustomerPortal):
    _items_per_page = 20

    def _donation_line_domain(self):
        partner = request.env.user.partner_id.commercial_partner_id
        return [
            ("donation_id.state", "=", "done"),
            ("donation_id.partner_id", "=", partner.id),
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "donation_count" in counters:
            values["donation_count"] = request.env["donation.line"].search_count(
                self._donation_line_domain()
            )
        return values

    @http.route(
        ["/my/donations", "/my/donations/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_donations(self, page=1, **kwargs):
        DonationLine = request.env["donation.line"]
        domain = self._donation_line_domain()
        line_count = DonationLine.search_count(domain)
        pager = portal_pager(
            url="/my/donations",
            total=line_count,
            page=page,
            step=self._items_per_page,
        )
        lines = DonationLine.search(
            domain,
            order="donation_date desc, id desc",
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        product_names = {line.id: line.sudo().product_id.display_name for line in lines}
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "lines": lines,
                "product_names": product_names,
                "page_name": "donations",
                "default_url": "/my/donations",
                "pager": pager,
            }
        )
        return request.render("donation_portal.portal_my_donations", values)
