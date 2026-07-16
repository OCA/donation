# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from pydantic import BaseModel


class DonationCreate(BaseModel):
    lastname: str
    firstname: str = None
    title: str = None
    email: str
    phone: str = None
    mobile: str = None
    company_id: int = None
    message: str = None
    notes_list: list = None
    country_code: str = None
    street: str = None
    street2: str = None
    zip: str = None
    city: str = None
