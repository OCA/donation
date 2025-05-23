# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    donation_ids = fields.One2many(
        "donation.donation", "bank_statement_id", string="Donations", readonly=True
    )
    donation_count = fields.Integer(
        compute="_compute_donation_count", string="# of Donations", compute_sudo=True
    )

    def _compute_donation_count(self):
        rg_res = self.env["donation.donation"].read_group(
            [("bank_statement_id", "in", self.ids)],
            ["bank_statement_id"],
            ["bank_statement_id"],
        )
        mapped_data = {
            x["bank_statement_id"][0]: x["bank_statement_id_count"] for x in rg_res
        }
        for stmt in self:
            stmt.donation_count = mapped_data.get(stmt.id, 0)

    def _prepare_donation_vals(self, stline, move_line, payment_mode):
        company = self.company_id
        if not company.donation_credit_transfer_product_id:
            raise UserError(
                _(
                    "Missing Product for Donations via Credit Transfer "
                    "on company '%s'."
                )
                % company.display_name
            )
        if not payment_mode:
            raise UserError(
                _(
                    "Missing inbound payment mode linked to the bank journal '%s' "
                    "configured with 'Link to Bank Account' set to 'Fixed'."
                )
                % self.journal_id.display_name
            )
        amount = move_line.credit
        line_vals = {
            "product_id": company.donation_credit_transfer_product_id.id,
            "quantity": 1,
            "unit_price": amount,
        }
        partner = stline.partner_id
        vals = {
            "company_id": company.id,
            "partner_id": partner.id,
            "tax_receipt_option": partner.commercial_partner_id.tax_receipt_option,
            "payment_mode_id": payment_mode.id,
            "currency_id": company.currency_id.id,
            "payment_ref": stline.payment_ref,
            "check_total": amount,
            "donation_date": stline.date,
            "campaign_id": False,
            "bank_statement_line_id": stline.id,
            "line_ids": [(0, 0, line_vals)],
        }
        return vals

    def create_donations(self):
        self.ensure_one()
        ddo = self.env["donation.donation"]
        transit_account = self.journal_id.donation_account_id
        company_cur = self.company_id.currency_id
        if not transit_account:
            logger.info(
                "Journal %s doesn't have a donation transit account. "
                "Skip creation of donations." % self.journal_id.display_name
            )
            return False
        logger.info(
            "Trying to create donations for statement %s. Transit account=%s",
            self.display_name,
            transit_account.display_name,
        )
        payment_mode = self.env["account.payment.mode"].search(
            [
                ("bank_account_link", "=", "fixed"),
                ("company_id", "=", self.company_id.id),
                ("payment_type", "=", "inbound"),
                ("fixed_journal_id", "=", self.journal_id.id),
                ("payment_method_code", "in", ("manual", "sepa_credit_transfer")),
            ],
            limit=1,
        )
        for stline in self.line_ids:
            if (
                self.currency_id.compare_amounts(stline.amount, 0) > 0
                and not stline.donation_ids
                and stline.move_id
            ):
                for mline in stline.move_id.line_ids:
                    if (
                        mline.account_id == transit_account
                        and company_cur.compare_amounts(mline.credit, 0) > 0
                        and not mline.reconciled
                    ):
                        if not stline.partner_id:
                            raise UserError(
                                _(
                                    "Missing partner on bank statement line "
                                    "'%s' dated %s with amount %s."
                                )
                                % (stline.payment_ref, stline.date, stline.amount)
                            )
                        vals = self._prepare_donation_vals(stline, mline, payment_mode)
                        donation = ddo.create(vals)
                        self.message_post(
                            body=_(
                                "Donation <a href=# data-oe-model=donation.donation "
                                "data-oe-id=%d>%s</a> dated %s created for partner "
                                "<a href=# data-oe-model=res.partner "
                                "data-oe-id=%d>%s</a>."
                            )
                            % (
                                donation.id,
                                donation.number,
                                format_date(self.env, donation.donation_date),
                                donation.partner_id.id,
                                donation.partner_id.display_name,
                            )
                        )

    def button_validate(self):
        super().button_validate()
        for stmt in self:
            stmt.create_donations()

    def show_donations(self):
        action = self.env.ref("donation.donation_action").sudo().read([])[0]
        action["domain"] = [("bank_statement_id", "in", self.ids)]
        return action


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    donation_ids = fields.One2many(
        "donation.donation", "bank_statement_line_id", string="Donations"
    )
