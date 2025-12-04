from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SignRequest(models.Model):
    _inherit = 'sign.request'

    def _check_signers_email(self):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return True
        return super()._check_signers_email() if hasattr(super(), '_check_signers_email') else True

    @api.constrains('request_item_ids')
    def _check_signers_have_email(self):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return
        if hasattr(super(), '_check_signers_have_email'):
            return super()._check_signers_have_email()

    def _validate_emails(self):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return True
        return super()._validate_emails() if hasattr(super(), '_validate_emails') else True

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle no_sign_mail context"""
        _logger.warning("=== SignRequest.create llamado ===")
        _logger.warning(f"Contexto en create: {self.env.context}")
        _logger.warning(f"no_sign_mail en contexto: {self.env.context.get('no_sign_mail')}")
        _logger.warning(f"vals_list: {vals_list}")

        if self.env.context.get('no_sign_mail'):
            _logger.warning("=== CREANDO SignRequest con contexto no_sign_mail ===")
            # Create a new context with all necessary flags
            ctx = dict(self.env.context or {})
            ctx.update({
                'mail_create_nosubscribe': True,
                'mail_create_nolog': True,
                'tracking_disable': True,
                'no_sign_mail': True,
            })
            _logger.warning(f"Contexto mejorado para SignRequest: {ctx}")

            # Process vals_list to ensure request_item_ids are created with the right context
            for vals in vals_list:
                if 'request_item_ids' in vals:
                    _logger.warning(f"request_item_ids detectado: {vals['request_item_ids']}")
                    # The request_item_ids will be created by the ORM,
                    # but we need to ensure our context is used
                    # Store the commands for later
                    request_item_commands = vals.get('request_item_ids', [])
                    vals['request_item_ids'] = request_item_commands

            # Call super with the enhanced context - this will create both
            # the sign.request and the sign.request.item records with our context
            _logger.warning("=== Llamando a super().create con contexto mejorado ===")
            result = super(SignRequest, self.with_context(**ctx)).create(vals_list)
            _logger.warning(f"=== SignRequest creado: {result} ===")
            return result

        _logger.warning("=== CREANDO SignRequest SIN contexto no_sign_mail ===")
        return super().create(vals_list)

    def send_signature_accesses(self):
        """Override to skip sending emails when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            # Don't send emails
            return True
        return super().send_signature_accesses()

    def _get_final_recipients(self):
        """Override to filter out False email values (partners without email)"""
        self.ensure_one()
        # Get all recipients but filter out False/empty emails
        signer_emails = set()
        for email in self.request_item_ids.mapped('signer_email'):
            if email and isinstance(email, str):  # Only add valid string emails
                signer_emails.add(email)

        cc_emails = set()
        for partner in self.cc_partner_ids.filtered(lambda p: p.email_formatted):
            if partner.email:
                cc_emails.add(partner.email)

        all_recipients = signer_emails | cc_emails
        return all_recipients

    def initialize_new(self):
        """Override to skip email sending when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            # Skip the initialization that sends emails
            return True
        return super().initialize_new() if hasattr(super(), 'initialize_new') else True

    def action_sent(self):
        """Override to skip email sending when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            # Don't send emails
            return True
        return super().action_sent() if hasattr(super(), 'action_sent') else True

