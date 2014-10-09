# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring Tax Receipt module for Odoo
#    Copyright (C) 2014 Artisanat Monastique de Provence www.barroux.org
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _


class donation_donation(orm.Model):
    _inherit = 'donation.donation'

    def _check_recurring_tax_receipt(self, cr, uid, ids):
        for donation in self.browse(cr, uid, ids):
            if (
                    donation.recurring_template
                    and donation.tax_receipt_option == 'each'):
                raise orm.except_orm(
                    _('Error:'),
                    _("The recurring donation of %s cannot have a tax "
                        "receipt option 'Each'.")
                    % donation.partner_id.name)
        return True

    _constraints = [(
        _check_recurring_tax_receipt,
        'Error in recurring donation template',
        ['recurring_template', 'tax_receipt_option']
    )]

    def recurring_template_change(
            self, cr, uid, ids, recurring_template, tax_receipt_option,
            partner_id, context=None):
        res = {'value': {}, 'warning': {}}
        if recurring_template and tax_receipt_option == 'each':
            res['value']['tax_receipt_option'] = 'annual'
            res['warning']['title'] = _('Update of Tax Receipt Option')
            res['warning']['message'] = _(
                "As it is a recurring donation, "
                "the Tax Receipt Option has been changed from Each to "
                "Annual. You may want to change it also on the Donor "
                "form.")
        if not recurring_template and partner_id:
            partner = self.pool['res.partner'].browse(
                cr, uid, partner_id, context=context)
            if partner.tax_receipt_option != tax_receipt_option:
                res['value']['tax_receipt_option'] = partner.tax_receipt_option
        return res
