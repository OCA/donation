# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from fastapi import HTTPException, status

from odoo import _, api, fields, models

logger = logging.getLogger(__name__)


UUID_VERSION = 4


class DonationDonation(models.Model):
    _inherit = "donation.donation"

    controller_mode = fields.Selection(
        [
            ("created", "Created"),
        ],
        readonly=True,
        string="Web Form Mode",
    )
    controller_firstname = fields.Char(tracking=True, string="Firstname")
    controller_lastname = fields.Char(tracking=True, string="Lastname")
    controller_title_id = fields.Many2one(
        "res.partner.title",
        domain=[("api_code", "!=", False)],
        string="Title",
        tracking=True,
    )
    controller_email = fields.Char(tracking=True, string="E-mail")
    controller_phone = fields.Char(tracking=True, string="Phone")
    controller_mobile = fields.Char(tracking=True, string="Mobile")
    controller_message = fields.Char(string="Donor Message")
    controller_notes = fields.Text(string="Web Form Other Information")
    controller_street = fields.Char(string="Address Line 1")
    controller_street2 = fields.Char(string="Address Line 2")
    controller_zip = fields.Char(string="ZIP")
    controller_city = fields.Char(string="City")
    controller_country_id = fields.Many2one("res.country", string="Country")

    @api.model
    def _controller_prepare_create_update(self, cobject, try_match_partner=True):
        assert cobject
        to_strip_fields = [
            "firstname",
            "lastname",
            "street",
            "street2",
            "zip",
            "city",
            "country_code",
            "email",
            "phone",
            "mobile",
        ]
        for to_strip_field in to_strip_fields:
            ini_value = getattr(cobject, to_strip_field)
            if isinstance(ini_value, str):
                setattr(cobject, to_strip_field, ini_value.strip() or False)
        notes_list = cobject.notes_list
        if not isinstance(notes_list, list):
            notes_list = []
        lastname = cobject.lastname
        if not lastname:  # Should never happen because checked by fastapi
            logger.error("Missing lastname in stay controller. Quitting.")
            return False
        firstname = cobject.firstname
        title_code = cobject.title
        title_id = False
        if title_code:
            # TODO set lang
            title = self.env["res.partner.title"].search(
                [("stay_code", "=", title_code)], limit=1
            )
            if title:
                title_id = title.id
            else:
                avail_title_read = self.env["res.partner.title"].search_read(
                    [("stay_code", "!=", False)], ["stay_code"]
                )
                avail_title_list = [x["stay_code"] for x in avail_title_read]
                error_msg = (
                    f"Wrong title: {title_code}. "
                    f"Possible values: {', '.join(avail_title_list)}."
                )
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg
                )
        email = cobject.email
        if not email:  # Should never happen because defined as required
            logger.error("Missing email in stay controller. Quitting.")
        # country
        country_id = False
        phone = cobject.phone
        mobile = cobject.mobile
        if cobject.country_code:
            country_code = cobject.country_code.upper()
            country = self.env["res.country"].search(
                [("code", "=", country_code)], limit=1
            )
            if country:
                country_id = country.id
                if phone:
                    phone = self.env["phone.validation.mixin"].phone_format(
                        phone, country=country
                    )
                    logger.info(
                        "Phone number reformatted from %s to %s (country %s)",
                        cobject.phone,
                        phone,
                        country.name,
                    )
                if mobile:
                    mobile = self.env["phone.validation.mixin"].phone_format(
                        mobile, country=country
                    )
                    logger.info(
                        "Mobile number reformatted from %s to %s (country %s)",
                        cobject.mobile,
                        mobile,
                        country.name,
                    )
            else:
                logger.warning("Country code %s doesn't exist in Odoo.", country_code)
                notes_list.append(
                    _("Country code %s doesn't exist in Odoo.") % country_code
                )

        vals = {
            "controller_message": cobject.message,
            "controller_firstname": firstname,
            "controller_lastname": lastname,
            "controller_email": email,
            "controller_phone": phone,
            "controller_mobile": mobile,
            "controller_title_id": title_id,
            "controller_street": cobject.street,
            "controller_street2": cobject.street2,
            "controller_zip": cobject.zip,
            "controller_city": cobject.city,
            "controller_country_id": country_id,
            "controller_notes": "\n".join(notes_list),
        }
        if try_match_partner:
            vals["partner_id"] = self._controller_try_match_partner(vals)
        return vals
