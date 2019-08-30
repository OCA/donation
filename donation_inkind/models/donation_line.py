from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class DonationLine(models.Model):
    _inherit = 'donation.line'

    product_uom = fields.Many2one(
        'product.uom',
        string='Product Unit of Measure'
    )
    move_dest_ids = fields.One2many(
        'stock.move',
        'created_donation_line_id',
        'Downstream Moves'
    )
    move_ids = fields.One2many(
        'stock.move',
        'donation_line_id',
        string='Reservation',
        readonly=True,
        ondelete='set null',
        copy=False
    )

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                done += moves.create(val)
        return done

    @api.multi
    def _get_stock_move_unit_price(self):
        self.ensure_one()
        line = self[0]
        order = line.donation_id
        unit_price = line.unit_price
        if line.product_uom.id != line.product_id.uom_id.id:
            unit_price *= (
                line.product_uom.factor / line.product_id.uom_id.factor
            )
        return unit_price

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line.
        This function returns a list of dictionary ready to be used
        in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        donation = self.donation_id
        warehouse = donation.picking_type_id.warehouse_id
        unit_price = self._get_stock_move_unit_price()
        for move in self.move_ids.filtered(
            lambda x: x.state != 'cancel' and
            not x.location_dest_id.usage == "supplier"
        ):
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty,
                self.product_uom,
                rounding_method='HALF-UP'
            )
        template = {
            'name': self.display_name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': donation.donation_date,
            'date_expected': fields.Date.today(),
            'location_id': donation.partner_id.property_stock_supplier.id,
            'location_dest_id': donation._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': donation.partner_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'company_id': donation.company_id.id,
            'donation_line_id': self.id,
            'unit_price': unit_price,
            'picking_type_id': donation.picking_type_id.id,
            'group_id': donation.group_id.id,
            'origin': donation.display_name,
            'route_ids': (
                warehouse and
                [(6, 0, [x.id for x in warehouse.route_ids])] or []
            ),
            'warehouse_id': warehouse.id,
        }
        diff_quantity = self.quantity - qty
        if float_compare(
            diff_quantity,
            0.0,
            precision_rounding=self.product_uom.rounding
        ) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if (
                self.product_uom.id != quant_uom.id and
                get_param('stock.propagate_uom') != '1'
            ):
                product_qty = self.product_uom._compute_quantity(
                    diff_quantity,
                    quant_uom,
                    rounding_method='HALF-UP'
                )
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = diff_quantity
            res.append(template)
        return res
