# © 2019 Benjamin Brich <@>
# © 2019 Thore Baden <thorebaden@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('donation', 'type')
    def donation_check(self):
        for product in self:
            if (
                product.donation and
                product.type != 'product' and
                product.type != 'consu'
            ):
                super().donation_check()
