# Copyright 2014-2016 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2016 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class DonationCampaign(models.Model):
    _name = 'donation.campaign'
    _description = 'Code attributed for a Donation Campaign'
    _order = 'code'

    @api.depends('code', 'name')
    def name_get(self):
        res = []
        for camp in self:
            name = camp.name
            if camp.code:
                name = u'[%s] %s' % (camp.code, name)
            res.append((camp.id, name))
        return res

    code = fields.Char('Code')
    name = fields.Char(
        'Name',
        required=True
    )
    start_date = fields.Date(
        'Start Date',
        default=fields.Date.context_today
    )
    note = fields.Text('Notes', oldname='nota')
