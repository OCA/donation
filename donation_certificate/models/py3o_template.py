from odoo import fields, models, api
from base64 import b64encode
# import sys
import pkg_resources
# import os


class Py3oTemplate(models.Model):
    _inherit = "py3o.template"

    py3o_template_fallback = fields.Char(
        "Fallback",
        size=128,
        help=(
            "If the user does not provide a template this will be used "
            "it should be a relative path to root of YOUR module "
            "or an absolute path on your server."
        ),
    )

    @api.model_create_multi
    def create(self, vals_list):
        module = "donation_certificate"
        vals = vals_list[0]
        if vals['py3o_template_fallback']:
            flbk_filename = pkg_resources.resource_filename(
                "odoo.addons.%s" % module, vals['py3o_template_fallback']
            )
            with open(flbk_filename, "rb") as tmpl:
                tmpl_data = b64encode(tmpl.read())
            vals['py3o_template_data'] = tmpl_data
        #     if not rec.py3o_template_data:
        #         rec.py3o_template_data = False
        return super().create([vals])
