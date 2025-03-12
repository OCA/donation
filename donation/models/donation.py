# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

from odoo.addons.account import _auto_install_l10n

logger = logging.getLogger(__name__)


class DonationDonation(models.Model):
    _name = "donation.donation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Donation"
    _order = "id desc"
    _check_company_auto = True

    @api.depends(
        "line_ids.unit_price",
        "line_ids.quantity",
        "line_ids.product_id",
        "donation_date",
        "currency_id",
        "company_id",
    )
    def _compute_total(self):
        for donation in self:
            total = tax_receipt_total = 0.0
            for line in donation.line_ids:
                line_total = line.quantity * line.unit_price
                total += line_total
                if line.tax_receipt_ok:
                    tax_receipt_total += line_total

            date = donation.donation_date or fields.Date.context_today(self)
            donation.amount_total = total
            donation_currency = donation.currency_id
            company_currency = donation.company_id.currency_id
            total_company_currency = donation_currency._convert(
                total, company_currency, donation.company_id, date
            )
            tax_receipt_total_cc = donation_currency._convert(
                tax_receipt_total,
                company_currency,
                donation.company_id,
                date,
            )
            donation.amount_total_company_currency = total_company_currency
            donation.tax_receipt_total = tax_receipt_total_cc

    # We don't want a depends on partner_id.country_id, because if the partner
    # moves to another country, we want to keep the old country for
    # past donations to have good statistics
    @api.depends("partner_id")
    def _compute_country_id(self):
        for donation in self:
            donation.country_id = donation.partner_id.country_id

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        states={"done": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
        default=lambda self: self.env.company.currency_id,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Donor",
        required=True,
        index=True,
        states={"done": [("readonly", True)]},
        tracking=True,
        ondelete="restrict",
    )
    commercial_partner_id = fields.Many2one(
        related="partner_id.commercial_partner_id",
        string="Parent Donor",
        store=True,
        index=True,
    )
    # country_id is here to have stats per country
    # WARNING : I can't put a related field, because when someone
    # writes on the country_id of a partner, it will trigger a write
    # on all it's donations, including donations in other companies
    # which will be blocked by the record rule
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        compute="_compute_country_id",
        store=True,
        readonly=True,
    )
    check_total = fields.Monetary(
        string="Check Amount",
        states={"done": [("readonly", True)]},
        currency_field="currency_id",
        tracking=True,
    )
    amount_total = fields.Monetary(
        compute="_compute_total",
        string="Amount Total",
        currency_field="currency_id",
        store=True,
        readonly=True,
        tracking=True,
    )
    amount_total_company_currency = fields.Monetary(
        compute="_compute_total",
        string="Amount Total in Company Currency",
        currency_field="company_currency_id",
        store=True,
        readonly=True,
    )
    donation_date = fields.Date(
        string="Donation Date",
        required=True,
        states={"done": [("readonly", True)]},
        index=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        states={"done": [("readonly", True)]},
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        "donation.line",
        "donation_id",
        string="Donation Lines",
        states={"done": [("readonly", True)]},
        copy=True,
    )
    move_id = fields.Many2one(
        "account.move",
        string="Account Move",
        readonly=True,
        copy=False,
        check_company=True,
    )
    number = fields.Char(
        required=True,
        copy=False,
        string="Donation Number",
        index=True,
        default=lambda self: _("New"),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        domain="[('company_id', '=', company_id), ('donation', '=', True)]",
        tracking=True,
        check_company=True,
        states={"done": [("readonly", True)]},
        default=lambda self: self.env.user.context_donation_payment_mode_id,
    )
    payment_ref = fields.Char(
        string="Payment Reference",
        states={"done": [("readonly", True)]},
        copy=False,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancel", "Cancelled")],
        string="State",
        readonly=True,
        copy=False,
        default="draft",
        index=True,
        tracking=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        store=True,
    )
    campaign_id = fields.Many2one(
        "donation.campaign",
        string="Donation Campaign",
        tracking=True,
        check_company=True,
        ondelete="restrict",
        default=lambda self: self.env.user.context_donation_campaign_id,
    )
    tax_receipt_id = fields.Many2one(
        "donation.tax.receipt",
        string="Tax Receipt",
        readonly=True,
        copy=False,
        tracking=True,
        check_company=True,
    )
    tax_receipt_option = fields.Selection(
        [
            ("none", "None"),
            ("each", "For Each Donation"),
            ("annual", "Annual Tax Receipt"),
        ],
        string="Tax Receipt Option",
        states={"done": [("readonly", True)]},
        index=True,
        tracking=True,
    )
    tax_receipt_total = fields.Monetary(
        compute="_compute_total",
        string="Tax Receipt Eligible Amount",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
        help="Eligible Tax Receipt Sub-total in Company Currency",
    )
    bank_statement_line_id = fields.Many2one(
        "account.bank.statement.line",
        string="Source Bank Statement Line",
        ondelete="restrict",
        readonly=True,
    )
    bank_statement_id = fields.Many2one(
        related="bank_statement_line_id.statement_id",
        string="Bank Statement",
        store=True,
    )
    thanks_printed = fields.Boolean(
        string="Thanks Printed",
        copy=False,
        tracking=True,
        help="This field automatically becomes active when "
        "the thanks letter has been printed.",
    )
    thanks_template_id = fields.Many2one(
        "donation.thanks.template",
        string="Thanks Template",
        ondelete="restrict",
        copy=False,
    )

    _sql_constraints = [
        (
            "bank_statement_line_uniq",
            "unique(bank_statement_line_id)",
            "A donation already exists for this bank statement line.",
        )
    ]

    @api.model
    def create(self, vals):
        if "company_id" in vals:
            self = self.with_company(vals["company_id"])
        if vals.get("number", _("New")) == _("New"):
            vals["number"] = self.env["ir.sequence"].next_by_code(
                "donation.donation", sequence_date=vals.get("donation_date")
            ) or _("New")
        return super().create(vals)

    def _prepare_each_tax_receipt(self):
        self.ensure_one()
        vals = {
            "company_id": self.company_id.id,
            "currency_id": self.company_currency_id.id,
            "donation_date": self.donation_date,
            "amount": self.tax_receipt_total,
            "type": "each",
            "partner_id": self.commercial_partner_id.id,
        }
        return vals

    # TODO migration: remove 'journal' argument and use self.payment_mode_id.fixed_journal_id
    def _prepare_counterpart_move_line(
        self, total_company_cur, total_currency, journal
    ):
        self.ensure_one()
        journal = self.payment_mode_id.fixed_journal_id
        if self.company_currency_id.compare_amounts(total_company_cur, 0) > 0:
            debit = total_company_cur
            credit = 0
        else:
            credit = -total_company_cur
            debit = 0
        if self.bank_statement_line_id:
            account_id = journal.donation_account_id.id
        else:
            if not journal.payment_debit_account_id:
                raise UserError(
                    _("Missing Outstanding Receipts Account on journal '%s'.")
                    % journal.display_name
                )
            account_id = journal.payment_debit_account_id.id
        vals = {
            "debit": debit,
            "credit": credit,
            "account_id": account_id,
            "partner_id": self.commercial_partner_id.id,
            "currency_id": self.currency_id.id,
            "amount_currency": total_currency,
            "name": self.number,
        }
        return vals

    def _prepare_donation_move(self):
        self.ensure_one()
        if not self.bank_statement_line_id and not self.payment_mode_id.donation:
            raise UserError(
                _(
                    "The payment mode '%s' selected on donation %s "
                    "is not a donation payment mode."
                )
                % (self.payment_mode_id.display_name, self.number)
            )
        assert self.payment_mode_id.bank_account_link == "fixed"
        journal = self.payment_mode_id.fixed_journal_id
        assert journal

        # Note : we can have negative donations for donors that use direct
        # debit when their direct debit rejected by the bank
        total_company_cur = 0.0
        total_currency = 0.0

        aml = defaultdict(float)
        # key = (account_id, analytic_account_id)
        # value = {'credit': ..., 'debit': ..., 'amount_currency': ...}
        for line in self.line_ids:
            if line.in_kind:
                continue
            if self.currency_id.is_zero(line.amount):
                continue
            account_id = line._get_account_id()
            if not account_id:
                raise UserError(
                    _("Failed to get account for donation line with product '%s'.")
                    % line.product_id.display_name
                )
            analytic_account_id = line._get_analytic_account_id()
            aml[(account_id, analytic_account_id)] += line.amount

        if not aml:
            return False

        vals = {
            "company_id": self.company_id.id,
            "journal_id": journal.id,
            "date": self.donation_date,
            "ref": self.payment_ref,
            "line_ids": [],
        }

        for (account_id, analytic_account_id), amount in aml.items():
            total_currency += amount
            amount_cc = self.currency_id._convert(
                amount, self.company_currency_id, self.company_id, self.donation_date
            )
            total_company_cur += amount_cc
            if self.company_currency_id.compare_amounts(amount_cc, 0) > 0:
                credit = amount_cc
                debit = 0
            else:
                debit = -amount_cc
                credit = 0
            vals["line_ids"].append(
                (
                    0,
                    0,
                    {
                        "credit": credit,
                        "debit": debit,
                        "account_id": account_id,
                        "analytic_account_id": analytic_account_id,
                        "partner_id": self.commercial_partner_id.id,
                        "currency_id": self.currency_id.id,
                        "amount_currency": -amount,
                        "name": self.number,
                    },
                )
            )

        # counter-part
        ml_vals = self._prepare_counterpart_move_line(
            total_company_cur, total_currency, journal
        )
        vals["line_ids"].append((0, 0, ml_vals))
        return vals

    def validate(self):
        check_total = self.env["res.users"].has_group(
            "donation.group_donation_check_total"
        )
        for donation in self:
            if donation.donation_date > fields.Date.context_today(self):
                raise UserError(
                    _(
                        "The date of donation %s should be today "
                        "or in the past, not in the future!"
                    )
                    % donation.number
                )
            if not donation.line_ids:
                raise UserError(
                    _(
                        "Cannot validate donation %s because it doesn't "
                        "have any lines!"
                    )
                    % donation.number
                )

            if donation.currency_id.is_zero(donation.amount_total):
                raise UserError(
                    _("Cannot validate donation %s because the " "total amount is 0!")
                    % donation.number
                )

            if donation.state != "draft":
                raise UserError(
                    _(
                        "Cannot validate donation %s because it is not "
                        "in draft state."
                    )
                    % donation.number
                )

            if check_total and donation.currency_id.compare_amounts(
                donation.check_total, donation.amount_total
            ):
                raise UserError(
                    _(
                        "The amount of donation %s (%s) is different "
                        "from the sum of the donation lines (%s)."
                    )
                    % (
                        donation.number,
                        format_amount(
                            self.env, donation.check_total, donation.currency_id
                        ),
                        format_amount(
                            self.env, donation.amount_total, donation.currency_id
                        ),
                    )
                )
            full_in_kind = all([line.in_kind for line in donation.line_ids])
            if not donation.payment_mode_id and not full_in_kind:
                raise UserError(
                    _(
                        "Payment Mode is not set on donation %s (only fully "
                        "in-kind donations don't require a payment mode)."
                    )
                    % donation.number
                )

            vals = {"state": "done"}
            if full_in_kind and donation.payment_mode_id:
                vals["payment_mode_id"] = False

            if not full_in_kind:
                move_vals = donation._prepare_donation_move()
                # when we have a full in-kind donation: no account move
                if move_vals:
                    move = self.env["account.move"].sudo().create(move_vals)
                    move.sudo().action_post()
                    vals["move_id"] = move.id
            else:
                donation.message_post(
                    body=_("Full in-kind donation: no account move generated")
                )

            receipt = donation.generate_each_tax_receipt()
            if receipt:
                vals["tax_receipt_id"] = receipt.id

            donation.write(vals)
            if donation.bank_statement_line_id:
                donation.sudo()._reconcile_donation_from_bank_statement()
            donation.partner_id._update_donor_rank()
        return

    def _reconcile_donation_from_bank_statement(self):
        self.ensure_one()
        mlines_to_reconcile = self.env["account.move.line"]
        journal = self.payment_mode_id.fixed_journal_id
        if not journal:
            raise UserError(
                _(
                    "Donation %s is linked to a bank statement line, "
                    "but its payment mode '%s' doesn't have a fixed link "
                    "to a bank journal. This should never happen."
                )
                % (self.number, self.payment_mode_id.display_name)
            )
        transit_account = journal.donation_account_id
        if not transit_account:
            raise UserError(
                _(
                    "Donation %s is linked to a bank statement line, but "
                    "the journal '%s' linked to its payment mode '%s' "
                    "doesn't have a donation by credit transfer account. "
                    "This should never happen."
                )
                % (self.number, journal.display_name, self.payment_mode_id.display_name)
            )
        if not transit_account.reconcile:
            raise UserError(
                _(
                    "Donation %s is linked to a bank statement line, but "
                    "the donation by credit transfer account '%s' configured on "
                    "the journal '%s' linked to its payment mode '%s' "
                    "is not reconciliable. This should never happen."
                )
                % (
                    self.number,
                    transit_account.display_name,
                    journal.display_name,
                    self.payment_mode_id.display_name,
                )
            )

        for donation_mline in self.move_id.line_ids:
            if (
                donation_mline.account_id == transit_account
                and not donation_mline.reconciled
            ):
                mlines_to_reconcile |= donation_mline
                logger.info(
                    "Found donation move line to reconcile ID=%d" % donation_mline.id
                )
                break
        for statement_mline in self.bank_statement_line_id.move_id.line_ids:
            if (
                statement_mline.account_id == transit_account
                and not statement_mline.reconciled
            ):
                mlines_to_reconcile |= statement_mline
                logger.info(
                    "Found bank statement move line to reconcile " "ID=%d",
                    statement_mline.id,
                )
                break
        if len(mlines_to_reconcile) == 2:
            mlines_to_reconcile.reconcile()
            logger.info(
                "Successfull reconcilation between donation and " "bank statement."
            )

    def generate_each_tax_receipt(self):
        self.ensure_one()
        receipt = False
        if (
            self.tax_receipt_option == "each"
            and not self.tax_receipt_id
            and not self.company_currency_id.is_zero(self.tax_receipt_total)
        ):
            receipt_vals = self._prepare_each_tax_receipt()
            receipt = self.env["donation.tax.receipt"].create(receipt_vals)
        return receipt

    def save_default_values(self):
        self.ensure_one()
        self.env.user.write(
            {
                "context_donation_payment_mode_id": self.payment_mode_id.id,
                "context_donation_campaign_id": self.campaign_id.id,
            }
        )

    def done2cancel(self):
        """from Done state to Cancel state"""
        for donation in self:
            if donation.tax_receipt_id:
                raise UserError(
                    _(
                        "You cannot cancel this donation because "
                        "it is linked to the tax receipt %s. You should first "
                        "delete this tax receipt (but it may not be legally "
                        "allowed)."
                    )
                    % donation.tax_receipt_id.number
                )
            if donation.sudo().move_id:
                donation.move_id.sudo().button_cancel()
                donation.with_context(force_delete=True).sudo().move_id.unlink()
            donation.write({"state": "cancel"})
            donation.partner_id._update_donor_rank()

    def cancel2draft(self):
        """from Cancel state to Draft state"""
        for donation in self:
            if donation.move_id:
                raise UserError(
                    _("A cancelled donation should not be linked to an account move")
                )
            if donation.tax_receipt_id:
                raise UserError(
                    _("A cancelled donation should not be linked to a tax receipt")
                )
        self.write({"state": "draft"})

    def unlink(self):
        for donation in self:
            if donation.state == "done":
                raise UserError(
                    _("The donation '%s' is in Done state, so you cannot delete it.")
                    % donation.display_name
                )
            if donation.move_id:
                raise UserError(
                    _(
                        "The donation '%s' is linked to an account move, "
                        "so you cannot delete it."
                    )
                    % donation.display_name
                )
            if donation.tax_receipt_id:
                raise UserError(
                    _(
                        "The donation '%s' is linked to the tax receipt %s, "
                        "so you cannot delete it."
                    )
                    % (donation.display_name, donation.tax_receipt_id.number)
                )
        return super().unlink()

    @api.depends("state", "number")
    def name_get(self):
        res = []
        for donation in self:
            name = donation.number
            if donation.state != "done":
                display_state = donation._fields["state"].convert_to_export(
                    donation.state, donation
                )
                name = "%s (%s)" % (name, display_state)
            res.append((donation.id, name))
        return res

    @api.onchange("partner_id")
    def partner_id_change(self):
        if self.partner_id:
            self.tax_receipt_option = (
                self.partner_id.commercial_partner_id.tax_receipt_option
            )

    @api.onchange("tax_receipt_option")
    def tax_receipt_option_change(self):
        res = {}
        if (
            self.partner_id
            and self.partner_id.commercial_partner_id.tax_receipt_option == "annual"
            and self.tax_receipt_option != "annual"
        ):
            res = {
                "warning": {
                    "title": _("Error:"),
                    "message": _(
                        "You cannot change the Tax Receipt Option when it is Annual."
                    ),
                },
            }
            self.tax_receipt_option = "annual"
        return res

    def print_thanks(self):
        self.ensure_one()
        self.write({"thanks_printed": True})
        action = (
            self.env.ref("donation.report_thanks")
            .with_context({"discard_logo_check": True})
            .report_action(self)
        )
        return action

    def thanks_printed_button(self):
        self.write({"thanks_printed": True})

    @api.model
    def auto_install_l10n(self):
        """Helper function for calling a method that is not accessible directly
        from XML data.
        """
        _auto_install_l10n(self.env.cr, None)


class DonationLine(models.Model):
    _name = "donation.line"
    _description = "Donation Lines"
    _rec_name = "product_id"
    _check_company_auto = True

    @api.depends(
        "unit_price",
        "quantity",
        "product_id",
        "donation_id.currency_id",
        "donation_id.donation_date",
        "donation_id.company_id",
    )
    def _compute_amount(self):
        for line in self:
            amount = line.quantity * line.unit_price
            line.amount = amount
            donation_currency = line.donation_id.currency_id
            date = line.donation_id.donation_date or fields.Date.context_today(self)
            amount_company_currency = donation_currency._convert(
                amount,
                line.donation_id.company_id.currency_id,
                line.donation_id.company_id,
                date,
            )
            tax_receipt_amount_cc = 0.0
            if line.product_id.tax_receipt_ok:
                tax_receipt_amount_cc = amount_company_currency
            line.amount_company_currency = amount_company_currency
            line.tax_receipt_amount = tax_receipt_amount_cc

    donation_id = fields.Many2one("donation.donation", "Donation", ondelete="cascade")
    currency_id = fields.Many2one(
        "res.currency",
        related="donation_id.currency_id",
    )
    company_id = fields.Many2one(related="donation_id.company_id", store=True)
    company_currency_id = fields.Many2one(
        "res.currency",
        related="donation_id.company_id.currency_id",
        string="Company Currency",
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        required=True,
        domain=[("donation", "=", True)],
        ondelete="restrict",
        check_company=True,
    )
    quantity = fields.Integer("Quantity", default=1)
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    amount = fields.Monetary(
        compute="_compute_amount",
        string="Amount",
        currency_field="currency_id",
        store=True,
    )
    amount_company_currency = fields.Monetary(
        compute="_compute_amount",
        string="Amount in Company Currency",
        currency_field="company_currency_id",
        store=True,
    )
    tax_receipt_amount = fields.Monetary(
        compute="_compute_amount",
        string="Tax Receipt Eligible Amount",
        currency_field="company_currency_id",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        "Analytic Account",
        ondelete="restrict",
        check_company=True,
    )
    sequence = fields.Integer("Sequence")
    # for the fields tax_receipt_ok and in_kind, we made an important change
    # between v8 and v9: in v8, it was a reglar field set by an onchange
    # in v9, it is a related stored field
    tax_receipt_ok = fields.Boolean(
        related="product_id.tax_receipt_ok",
        store=True,
    )
    in_kind = fields.Boolean(
        related="product_id.in_kind_donation",
        store=True,
        string="In Kind",
    )

    @api.onchange("product_id")
    def product_id_change(self):
        for line in self:
            if line.product_id and line.product_id.list_price:
                # We should change that one day...
                line.unit_price = line.product_id.list_price

    def _get_analytic_account_id(self):
        # Method designed to be inherited in custom module
        self.ensure_one()
        return self.analytic_account_id.id or False

    def _get_account_id(self):
        # Method designed to be inherited (in donation_mass for example)
        self.ensure_one()
        account = self.with_company(
            self.company_id.id
        ).product_id._get_product_accounts()["income"]
        return account.id
