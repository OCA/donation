from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError


class Donation(models.Model):
    _inherit = 'donation.donation'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    picking_ids = fields.Many2many(
        'stock.picking',
        compute='_compute_picking',
        string='Receptions',
        copy=False,
        store=True,
        compute_sudo=True
    )
    picking_count = fields.Integer(
        compute='_compute_picking',
        string='Receptions',
        default=0,
        store=True,
        compute_sudo=True
    )

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = (
            self.env.context.get('company_id') or
            self.env.user.company_id.id
        )
        types = type_obj.search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', company_id)
        ])
        if not types:
            types = type_obj.search([
                ('code', '=', 'incoming'),
                ('warehouse_id', '=', False)
            ])
        return types[:1]

    picking_type_id = fields.Many2one(
        'stock.picking.type',
        'Deliver To',
        states=READONLY_STATES,
        required=True,
        default=_default_picking_type,
        help="This will determine operation type of incoming shipment"
    )
    group_id = fields.Many2one(
        'procurement.group',
        string="Procurement Group",
        copy=False
    )
    dest_address_id = fields.Many2one(
        'res.partner',
        string='Drop Ship Address',
        states=READONLY_STATES,
        help="Put an address if you want to deliver directly from the vendor to the customer. "\
             "Otherwise, keep empty to deliver to your own company."
    )

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        #choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

    @api.depends('line_ids.move_ids.returned_move_ids',
                 'line_ids.move_ids.state',
                 'line_ids.move_ids.picking_id')
    def _compute_picking(self):
        for donation in self:
            pickings = self.env['stock.picking']
            for line in donation.line_ids:
                # We keep a limited scope on purpose. Ideally,
                # we should also use move_orig_ids and
                # do some recursive search,
                # but that could be prohibitive if not done correctly.
                moves = (
                    line.move_ids |
                    line.move_ids.mapped('returned_move_ids')
                )
                pickings |= moves.mapped('picking_id')
            donation.picking_ids = pickings
            donation.picking_count = len(pickings)

    def validate(self):
        check_total = self.env['res.users'].has_group(
            'donation.group_donation_check_total')
        for donation in self:
            if not donation.line_ids:
                raise UserError(_(
                    "Cannot validate the donation of %s because it doesn't "
                    "have any lines!") % donation.partner_id.name)

            if float_is_zero(
                    donation.amount_total,
                    precision_rounding=donation.currency_id.rounding):
                raise UserError(_(
                    "Cannot validate the donation of %s because the "
                    "total amount is 0 !") % donation.partner_id.name)

            if donation.state != 'draft':
                raise UserError(_(
                    "Cannot validate the donation of %s because it is not "
                    "in draft state.") % donation.partner_id.name)

            if check_total and float_compare(
                    donation.check_total, donation.amount_total,
                    precision_rounding=donation.currency_id.rounding):
                raise UserError(_(
                    "The amount of the donation of %s (%s) is different "
                    "from the sum of the donation lines (%s).") % (
                    donation.partner_id.name, donation.check_total,
                    donation.amount_total))

            vals = {'state': 'done'}

            if not float_is_zero(
                    donation.amount_total,
                    precision_rounding=donation.currency_id.rounding):
                move_vals = donation._prepare_donation_move()
                # when we have a full in-kind donation: no account move
                if move_vals:
                    move = self.env['account.move'].create(move_vals)
                    move.post()
                    vals['move_id'] = move.id
                else:
                    donation.message_post(_(
                        'Full in-kind donation: no account move generated'))

            receipt = donation.generate_each_tax_receipt()
            if receipt:
                vals['tax_receipt_id'] = receipt.id

            donation.write(vals)
            donation._create_picking()
        return

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        if self.dest_address_id:
            return self.dest_address_id.property_stock_customer.id
        return self.picking_type_id.default_location_dest_id.id

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.number,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(
                _("You must set a Vendor Location for this partner %s") %
                self.partner_id.name
            )
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.donation_date,
            'origin': self.number,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for donation in self:
            if any([ptype in ['product', 'consu'] for ptype in donation.line_ids.mapped('product_id.type')]):
                pickings = donation.picking_ids.filtered(
                    lambda x: x.state not in ('done', 'cancel')
                )
                if not pickings:
                    res = donation._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = donation.line_ids._create_stock_moves(picking)
                moves = moves.filtered(
                    lambda x: x.state not in ('done', 'cancel')
                )._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': picking, 'origin': donation},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True
