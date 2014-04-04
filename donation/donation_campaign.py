# -*- encoding: utf-8 -*-
##############################################################################
#
#    Donation module for OpenERP
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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class donation_campaign(orm.Model):
    _name = 'donation.campaign'
    _description = 'Code attributed for a Donation Campaign'

    _columns = {
        'code': fields.char('Code', size=10),
        'name': fields.char('Name', size=64, required=True),
        'campaign_creation_date': fields.date('Campaign Creation Date', readonly=True),
        'nota':fields.text('Notes'),
    }

    _defaults = {
        'campaign_creation_date' : fields.date.context_today,
        
    }
