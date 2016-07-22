# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import SUPERUSER_ID


def update_account_journal(cr, pool):
    ajo = pool['account.journal']
    journal_ids = ajo.search(
        cr, SUPERUSER_ID, [('type', 'in', ('bank', 'cash'))])
    if journal_ids:
        ajo.write(cr, SUPERUSER_ID, journal_ids, {'allow_donation': True})
    return
