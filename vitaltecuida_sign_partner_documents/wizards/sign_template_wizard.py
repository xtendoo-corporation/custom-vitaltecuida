from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError


class SignTemplateWizard(models.TransientModel):
    _name = 'sign.template.wizard'
    _description = 'Sign Template Wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        readonly=True,
        help='Contacto que firmará el documento'
    )

    sign_template_id = fields.Many2one(
        'sign.template',
        string='Plantilla de Firma',
        required=True,
        help='Seleccione la plantilla de firma a utilizar'
    )

    def action_sign_now(self):
        """Execute sign now action with the selected template and partner"""
        self.ensure_one()

        if not self.sign_template_id:
            raise UserError(_('Debe seleccionar una plantilla de firma.'))

        sign_template = self.sign_template_id

        # Get roles from template
        roles = sign_template.sign_item_ids.responsible_id.sorted()

        # Prepare signers list
        signers = []
        if roles:
            # Use the first role for our partner
            signers.append({
                'partner_id': self.partner_id.id,
                'role_id': roles[0].id,
                'mail_sent_order': 1,
            })
        else:
            # Use default role if no roles defined
            default_role = self.env.ref('sign.sign_item_role_default', raise_if_not_found=False)
            if default_role:
                signers.append({
                    'partner_id': self.partner_id.id,
                    'role_id': default_role.id,
                    'mail_sent_order': 1,
                })

        if not signers:
            raise UserError(_('No se pudo determinar el rol de firma. Por favor, configure la plantilla correctamente.'))

        # Create the sign request with request_item_ids
        sign_request = self.env['sign.request'].create({
            'template_id': sign_template.id,
            'request_item_ids': [Command.create({
                'partner_id': signer['partner_id'],
                'role_id': signer['role_id'],
                'mail_sent_order': signer['mail_sent_order'],
            }) for signer in signers],
            'reference': sign_template.display_name,
            'subject': _("Solicitud de Firma - %s", sign_template.attachment_id.name or sign_template.display_name),
        })

        # Open the signable document directly for the partner to sign
        return sign_request.go_to_signable_document(sign_request.request_item_ids)
