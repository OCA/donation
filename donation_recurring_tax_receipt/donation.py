# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Recurring Tax Receipt module for Odoo
#    Copyright (C) 2014-2015 Barroux Abbey (www.barroux.org)
#    Copyright (C) 2014-2015 Akretion France (www.akretion.com)
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

from openerp import models, api, _
from openerp.exceptions import Warning


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    @api.one
    @api.constrains('recurring_template', 'tax_receipt_option')
    def _check_recurring_tax_receipt(self):
        if self.recurring_template and self.tax_receipt_option == 'each':
            raise Warning(
                _("The recurring donation of %s cannot have a tax "
                    "receipt option 'Each'.")
                % self.partner_id.name)

    @api.onchange('recurring_template')
    def recurring_template_change(self):
        res = {'warning': {}}
        if self.recurring_template and self.tax_receipt_option == 'each':
            self.tax_receipt_option = 'annual'
            res['warning']['title'] = _('Update of Tax Receipt Option')
            res['warning']['message'] = _(
                "As it is a recurring donation, "
                "the Tax Receipt Option has been changed from Each to "
                "Annual. You may want to change it also on the Donor "
                "form.")
        if not self.recurring_template and self.partner_id:
            if self.partner_id.tax_receipt_option != self.tax_receipt_option:
                self.tax_receipt_option = self.partner_id.tax_receipt_option
        return res
