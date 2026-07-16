# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from pydantic import BaseModel


class DonationCreated(BaseModel):
    number: str
    id: int
    company_id: int
    phone: str = None
    mobile: str = None
    partner_id: int = None
