from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import get_lang


class Donation(models.Model):
    _inherit = "donation.donation"

    is_certificate_send = fields.Boolean(
        help="This field automatically becomes active when "
        "the thanks letter has been send.",
    )
    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        domain=[("res_model", "=", "donation.donation")],
        string="Attachments",
    )

    def action_send_certificate(self):
        self.ensure_one()
        if not self.tax_receipt_id and self.tax_receipt_option == "annual":
            raise ValidationError(_("Annual receipt has not been generated yet."))
        self.write({"is_certificate_send": True})
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref(
            "donation_certificate.donation_certificate_send_wizard_form",
            raise_if_not_found=False,
        )
        ctx = dict(
            default_model="donation.tax.receipt",
            default_res_id=self.tax_receipt_id.id,
            default_res_model="donation.tax.receipt",
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            mark_invoice_as_sent=True,
            default_email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
            force_email=True,
            active_ids=self.tax_receipt_id.ids,
        )
        report_action = {
            "name": _("Send Certificate"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "donation.certificate.send",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }
        return report_action

    def action_print_tax_receipt(self):
        """Print the certificate and mark it as sent, so that we can see more
        easily the next step of the workflow
        """
        self.filtered(lambda r: not r.is_certificate_send).write(
            {"is_certificate_send": True}
        )
        return self.env.ref(
            "donation_certificate.donation_certificate_report_py3o"
        ).report_action(self)

    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type
        """
        return "donation_certificate.email_template_donation_certificate"
