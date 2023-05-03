from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    contribution = fields.Float(
        string="Contribution",
    )

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrder, self).create_from_ui(orders)
        order_ids = self.browse(res)

        for o in orders:
            order_id = order_ids.filtered(
                lambda o_id: o_id.pos_reference == o.get("data").get("name")
            )
            try:
                order_id.contribution = o.get("data").get("contribution")
            except Exception:
                continue

        return res
