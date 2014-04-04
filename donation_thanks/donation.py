# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation Tax Receipt module for OpenERP
#    Copyright (C) 2014 Barroux Abbey
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

from openerp.osv import orm, fields


class donation_donation(orm.Model):
    _inherit = "donation.donation"

    _columns = {
        'thanks_printed': fields.boolean(
            'Thanks Printed',
            help="This field automatically becomes active when "
            "the thanks letter has been printed."),
        }

    def print_thanks(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "Only 1 ID for this button function"
        self.write(
            cr, uid, ids[0], {'thanks_printed': True}, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'donation.thanks',
            'datas': {'model': 'donation.donation', 'ids': ids},
            'context': context,
        }
