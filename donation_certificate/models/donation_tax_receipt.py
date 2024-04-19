from odoo import _, fields, models, api
from odoo.tools import get_lang


class DonationTaxReceipt(models.Model):
    _inherit = "donation.tax.receipt"

    is_certificate_send = fields.Boolean(
        help="This field automatically becomes active when "
        "the thanks letter has been send.",
    )
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'donation.tax.receipt')], string='Attachments')
    amount_donation = fields.Monetary(tracking=True, compute="_compute_amounts")
    amount_donation_in_kind_consu = fields.Monetary(tracking=True, compute="_compute_amounts")
    amount_donation_in_kind_service = fields.Monetary(tracking=True, compute="_compute_amounts")

    @api.depends('donation_ids')
    def _compute_amounts(self):
        for rec in self:
            amount_donation = 0
            amount_donation_in_kind_consu = 0
            amount_donation_in_kind_service = 0
            for donation in rec.donation_ids:
                for line in donation.line_ids:
                    if line.product_id.detailed_type == 'donation':
                        amount_donation = amount_donation + line.amount
                    elif line.product_id.detailed_type == 'donation_in_kind_consu':
                        amount_donation_in_kind_consu = amount_donation_in_kind_consu + line.amount
                    else:
                        amount_donation_in_kind_service = amount_donation_in_kind_service + line.amount
            rec.amount_donation = round(amount_donation, 2)
            rec.amount_donation_in_kind_consu = round(amount_donation_in_kind_consu, 2)
            rec.amount_donation_in_kind_service = round(amount_donation_in_kind_service, 2)

    def action_send_tax_receipt(self):
        self.write({"is_certificate_send": True})
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        compose_form = self.env.ref('donation_certificate.donation_certificate_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='donation.tax.receipt',
            default_res_model='donation.tax.receipt',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            default_email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
            force_email=True,
            active_ids=self.ids,
        )
        report_action = {
            'name': _('Send Certificate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'donation.certificate.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        return report_action

    def get_ref_report_name(self, lang):
        report_names = {
            'es_ES': "donation_certificate.donation_certificate_report_py3o_ES",
            'ca_ES': "donation_certificate.donation_certificate_report_py3o_CAT",
            'fr_FR': "donation_certificate.donation_certificate_report_py3o_FR",
            'en_GB': "donation_certificate.donation_certificate_report_py3o_EN"
        }

        return report_names.get(lang, "donation_certificate.donation_certificate_report_py3o_EN")

    def action_print_tax_receipt(self):
        """ Print the certificate and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        today = fields.Date.context_today(self)
        self.write({"print_date": today})
        self.filtered(lambda inv: not inv.is_certificate_send).write({'is_certificate_send': True})
        lang = get_lang(self.env).code
        report_action_py3o = self.get_ref_report_name(lang)
        return self.env.ref(report_action_py3o).report_action(self)

    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type
        """
        return (
            'donation_certificate.email_template_donation_certificate'
        )
