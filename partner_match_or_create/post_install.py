# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

logger = logging.getLogger(__name__)


def res_partner_title_postinstall(env):
    # set api_code on res.partner.title
    model_datas = env["ir.model.data"].search(
        [
            ("module", "=", "base"),
            ("model", "=", "res.partner.title"),
            ("res_id", "!=", False),
            ("name", "!=", False),
        ]
    )
    unique_code = set()
    for model_data in model_datas:
        api_code = model_data.name.split("_")[-1]
        if api_code in unique_code:
            logger.warning(
                "Skipping XMLID %s.%s because the suffix is not unique",
                model_data.module,
                model_data.name,
            )
            continue
        unique_code.add(api_code)
        title = env["res.partner.title"].browse(model_data.res_id)
        title.write({"api_code": api_code})
        logger.info(
            "Wrote api_code=%s on title %s ID %d",
            api_code,
            title.display_name,
            title.id,
        )
