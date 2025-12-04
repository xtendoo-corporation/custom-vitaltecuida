from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'

    skip_email_validation = fields.Boolean(
        string='Skip Email Validation',
        default=False,
        copy=False,
        help='Technical field to skip email validation for this sign request item'
    )

    @api.constrains('signer_email')
    def _check_signer_email_validity(self):
        """Override to skip email validation when no_sign_mail context is set or skip_email_validation is True"""
        _logger.warning("=== _check_signer_email_validity llamado ===")
        _logger.warning(f"Contexto completo: {self.env.context}")
        _logger.warning(f"no_sign_mail en contexto: {self.env.context.get('no_sign_mail')}")
        _logger.warning(f"Partner IDs: {self.mapped('partner_id.id')}")
        _logger.warning(f"Signer emails: {self.mapped('signer_email')}")
        _logger.warning(f"skip_email_validation flags: {self.mapped('skip_email_validation')}")

        # Check if any record has skip_email_validation flag
        if any(sri.skip_email_validation for sri in self):
            _logger.warning("=== SALTANDO validación de email por skip_email_validation flag ===")
            return

        if self.env.context.get('no_sign_mail'):
            _logger.warning("=== SALTANDO validación de email por no_sign_mail ===")
            return

        _logger.warning("=== EJECUTANDO validación de email (NO HAY no_sign_mail) ===")
        # Call parent constraint
        return super()._check_signer_email_validity()

    @api.constrains('partner_id')
    def _check_partner_email(self):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return
        if hasattr(super(), '_check_partner_email'):
            return super()._check_partner_email()

    @api.constrains('sign_request_id', 'partner_id', 'role_id')
    def _check_signers_validity(self):
        """Override to skip validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            # Still check roles but skip email validation
            self.sign_request_id.with_context(no_sign_mail=True)._check_signers_roles_validity()
            self.sign_request_id.with_context(no_sign_mail=True)._check_signers_partners_validity()
            return
        return super()._check_signers_validity()

    @api.depends('signer_email')
    def _compute_frame_hash(self):
        """Override to handle when signer_email is False (no email)"""
        from hashlib import sha256
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        for sri in self:
            if sri.partner_id and sri.signer_email:
                # Normal case: partner has email
                sri.frame_hash = sha256((sri.signer_email + db_uuid).encode()).hexdigest()
            elif sri.partner_id and not sri.signer_email:
                # Special case: partner without email (skip_email_validation)
                # Use partner_id as identifier instead of email
                sri.frame_hash = sha256((str(sri.partner_id.id) + db_uuid).encode()).hexdigest()
            else:
                # No partner (public user)
                sri.frame_hash = ''

    @api.depends('partner_id.email')
    def _compute_signer_email(self):
        """Override to ensure signer_email is always a string (never False)"""
        for sri in self:
            if sri.partner_id and sri.partner_id.email:
                # Partner has email - use it
                sri.signer_email = sri.partner_id.email
            else:
                # Partner has no email - use empty string instead of False
                sri.signer_email = ''

    def _check_email_before_send(self):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return True
        return super()._check_email_before_send() if hasattr(super(), '_check_email_before_send') else True

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle no_sign_mail context"""
        _logger.warning("=== SignRequestItem.create llamado ===")
        _logger.warning(f"Contexto en create: {self.env.context}")
        _logger.warning(f"no_sign_mail en contexto: {self.env.context.get('no_sign_mail')}")
        _logger.warning(f"vals_list: {vals_list}")

        if self.env.context.get('no_sign_mail'):
            _logger.warning("=== CREANDO con contexto no_sign_mail ===")
            # Mark all items to skip email validation
            for vals in vals_list:
                vals['skip_email_validation'] = True
                _logger.warning(f"Marcado skip_email_validation=True en vals: {vals}")

            # Create a new context with all necessary flags
            ctx = dict(self.env.context or {})
            ctx.update({
                'no_sign_mail': True,
                'mail_create_nosubscribe': True,
                'mail_create_nolog': True,
                'tracking_disable': True,
                'mail_notrack': True,
            })
            _logger.warning(f"Contexto mejorado: {ctx}")
            # Call super with the enhanced context
            return super(SignRequestItem, self.with_context(**ctx)).create(vals_list)

        _logger.warning("=== CREANDO SIN contexto no_sign_mail ===")
        return super().create(vals_list)

    def _send_signature_accesses(self):
        """Override to skip sending emails when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return True
        return super()._send_signature_accesses() if hasattr(super(), '_send_signature_accesses') else True

    def send_signature_accesses(self):
        """Override to skip sending emails when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            # Mark as sent but don't actually send
            self.write({'is_mail_sent': False})
            return True
        return super().send_signature_accesses()



