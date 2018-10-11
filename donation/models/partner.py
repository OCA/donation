# -*- coding: utf-8 -*-
# Copyright 2014-2016 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2016 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('donation_ids.partner_id')
    def _compute_donation_count(self):
        # The current user may not have access rights for donations
        for partner in self:
            try:
                partner.donation_count = len(partner.donation_ids)
            except Exception:
                partner.donation_count = 0

    donation_ids = fields.One2many(
        'donation.donation',
        'partner_id',
        string='Donations',
        readonly=True
    )
    donation_count = fields.Integer(
        compute='_compute_donation_count',
        string="# of Donations",
        readonly=True
    )
