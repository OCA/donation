# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import sys
from datetime import date, datetime, timedelta

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from odoo import _, api, tools

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import DonationCreate, DonationCreated

logger = logging.getLogger(__name__)

donation_api_router = APIRouter()


@donation_api_router.post("/new", response_model=DonationCreated, status_code=201)
def donation_new(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    donationcreate: DonationCreate,
) -> DonationCreated:
    logger.info("Donation controller /new called with staycreate=%s", donationcreate)
    env["donation.donation"]
    company_id = donationcreate.company_id
    if not company_id:
        company_str = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("donation.controller.company_id", False)
        )
        if company_str:
            try:
                company_id = int(company_str)
            except Exception as e:
                logger.warning(
                    "Failed to convert ir.config_parameter "
                    "stay.controller.company_id %s to int: %s",
                    company_str,
                    e,
                )
    if not company_id:
        company_id = env.ref("base.main_company").id
    # protection for DoS attacks
    limit_create_date = datetime.now() - timedelta(1)
    recent_draft_stay = sso.search_count(
        [
            ("company_id", "=", company_id),
            ("create_date", ">=", limit_create_date),
            ("state", "=", "draft"),
            ("controller_mode", "=", "created"),
        ]
    )
    recent_draft_stay_limit_str = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("stay.controller.max_requests_24h", 100)
    )
    recent_draft_stay_limit = int(recent_draft_stay_limit_str)
    logger.debug("recent_draft_stay=%d", recent_draft_stay)
    if recent_draft_stay > recent_draft_stay_limit and not tools.config.get(
        "test_enable"
    ):
        logger.error(
            "stay controller: %d draft stays created during the last 24h. "
            "Suspecting DoS attack. Request ignored.",
            recent_draft_stay,
        )
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    vals = sso._controller_prepare_create_update(staycreate)
    if not vals:
        return False

    arrival_date = staycreate.arrival_date
    departure_date = staycreate.departure_date
    if arrival_date < date.today():
        error_msg = f"Arrival date {arrival_date} cannot be in the past"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg
        )
    if departure_date < arrival_date:
        error_msg = (
            f"Departure date {departure_date} cannot be before "
            f"arrival date {arrival_date}"
        )
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg
        )
    guest_qty = staycreate.guest_qty
    if guest_qty < 1:
        error_msg = f"Guest quantity ({guest_qty}) must be strictly positive."
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg
        )

    vals.update(
        {
            "controller_mode": "created",
            "company_id": company_id,
            "group_id": staycreate.group_id or False,
            "guest_qty": guest_qty,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
        }
    )
    logger.debug("Creating new stay with vals=%s", vals)
    stay = sso.create(vals)
    logger.info("Create stay %s ID %d from controller", stay.display_name, stay.id)
    try:
        env.ref("stay_api.stay_controller_notify").sudo().with_context(
            action_description=_("created")
        ).send_mail(stay.id)
        logger.info("Mail sent for stay creation notification")
    except Exception as e:
        logger.error("Failed to generate stay creation email: %s", e)
    answer_dict = {
        "name": stay.name,
        "id": stay.id,
        "company_id": vals["company_id"],
        "partner_id": vals["partner_id"],
        "phone": vals["controller_phone"],
        "mobile": vals["controller_mobile"],
        "uuid": stay.controller_uuid,
    }
    logger.info("Stay controller /new answer: %s", answer_dict)
    return StayCreated(**answer_dict)
