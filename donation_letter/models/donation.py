from odoo import _, fields, models
from odoo.tools import get_lang


class Donation(models.Model):
    _inherit = "donation.donation"

    is_thanks_letter_send = fields.Boolean(
        default=False,
        help="This field automatically becomes active when "
        "the thanks letter has been send.",
    )
    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_id',
        domain=[('res_model', '=', 'donation.donation')],
        string='Attachments'
    )

    def action_send_thanks(self):
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        lang = False

        if len(self) == 1:
            lang = template._render_lang(self.ids)[self.id]

        if not lang:
            lang = get_lang(self.env).code

        compose_form = self.env.ref('donation_letter.donation_letter_send_wizard_form', raise_if_not_found=False)

        ctx = {
            'default_model': 'donation.donation',
            'default_res_model': 'donation.donation',
            'default_use_template': bool(template),
            'default_template_id': template and template.id or False,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'force_email': True,
            'active_ids': self.ids,
        }

        report_action = {
            'name': _('Send Thanks Letter'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'donation.letter.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

        return report_action


    def action_donation_print(self):
        """ Print the donation and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.filtered(lambda inv: not inv.is_thanks_letter_send).write({'is_thanks_letter_send': True})
        return self.env.ref('donation.report_thanks').report_action(self)

    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type
        """
        return (
            'donation_letter.email_template_thanks_letter'
        )
