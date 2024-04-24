# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"

    def _merge_results(self, reports_path):
        self.ensure_one()
        filetype = self.ir_actions_report_id.py3o_filetype
        if not reports_path:
            return False, False
        if len(reports_path) == 1:
            return reports_path[0], filetype
        else:
            return self._zip_results(reports_path), "zip"
