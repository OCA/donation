# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import FastAPI

from odoo import fields, models

from odoo.addons.fastapi.dependencies import (
    authenticated_partner_from_basic_auth_user,
    authenticated_partner_impl,
)

from ..routers import donation_api_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("donation", "Donation")], ondelete={"donation": "cascade"}
    )

    def _get_fastapi_routers(self):
        if self.app == "donation":
            return [donation_api_router]
        return super()._get_fastapi_routers()

    def _get_app(self) -> FastAPI:
        app = super()._get_app()
        if self.app == "donation":
            app.dependency_overrides[
                authenticated_partner_impl
            ] = authenticated_partner_from_basic_auth_user
        return app
