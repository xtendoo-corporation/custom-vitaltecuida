from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SignTemplateWizardNoEmail(models.TransientModel):
    _name = 'sign.template.wizard.no.email'
    _description = 'Sign Template Wizard (No Email Required)'

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
        """Execute sign now action with the selected template and partner (without email requirement)"""
        _logger.warning("=== action_sign_now llamado ===")
        self.ensure_one()

        if not self.sign_template_id:
            raise UserError(_('Debe seleccionar una plantilla de firma.'))

        sign_template = self.sign_template_id
        _logger.warning(f"Template seleccionado: {sign_template.display_name}")

        # Get roles from template
        roles = sign_template.sign_item_ids.responsible_id.sorted()
        _logger.warning(f"Roles encontrados: {roles.mapped('name')}")

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

        _logger.warning(f"Signers preparados: {signers}")
        _logger.warning(f"Partner: {self.partner_id.name} (ID: {self.partner_id.id})")
        _logger.warning(f"Partner email: {self.partner_id.email}")

        # Create context to disable all email validations and sending
        ctx = dict(self.env.context or {})
        ctx.update({
            'no_sign_mail': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'tracking_disable': True,
            'mail_notrack': True,
            'no_reset_password': True,
        })
        _logger.warning(f"=== Contexto creado: {ctx} ===")

        # Create the sign request with request_item_ids using Command.create
        # The context will be propagated through our overridden create methods
        _logger.warning("=== Iniciando creación de sign.request ===")
        sign_request = self.env['sign.request'].with_context(**ctx).create({
            'template_id': sign_template.id,
            'request_item_ids': [Command.create({
                'partner_id': signer['partner_id'],
                'role_id': signer['role_id'],
                'mail_sent_order': signer['mail_sent_order'],
            }) for signer in signers],
            'reference': sign_template.display_name,
            'subject': _("Solicitud de Firma - %s", sign_template.attachment_id.name or sign_template.display_name),
        })
        _logger.warning(f"=== sign.request creado: {sign_request} ===")

        # Open the signable document directly for the partner to sign
        # Make sure the context is maintained
        _logger.warning("=== Abriendo documento para firmar ===")
        return sign_request.with_context(**ctx).go_to_signable_document(sign_request.request_item_ids)

