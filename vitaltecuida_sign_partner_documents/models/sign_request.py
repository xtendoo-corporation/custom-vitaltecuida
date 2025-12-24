# pylint: disable=import-error, no-name-in-module
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class SignOcaRequest(models.Model):
    _inherit = 'sign.oca.request'

    def _check_signers_email(self):
        """OCA: omite validación de email si no_sign_mail en contexto"""
        if self.env.context.get('no_sign_mail'):
            return True
        return super()._check_signers_email() if hasattr(super(), '_check_signers_email') else True

    @api.constrains('signer_ids')
    def _check_signers_have_email(self):
        """OCA: omite validación de email si no_sign_mail en contexto"""
        if self.env.context.get('no_sign_mail'):
            return
        if hasattr(super(), '_check_signers_have_email'):
            return super()._check_signers_have_email()

    def _validate_emails(self):
        """OCA: omite validación de email si no_sign_mail en contexto"""
        if self.env.context.get('no_sign_mail'):
            return True
        return super()._validate_emails() if hasattr(super(), '_validate_emails') else True

    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('SignOcaRequest.create llamado')
        _logger.warning(f'Contexto en create: {self.env.context}')
        _logger.warning(f'vals_list: {vals_list}')
        return super().create(vals_list)

    def send_signature_accesses(self):
        if self.env.context.get('no_sign_mail'):
            return True
        return super().send_signature_accesses()

    def _get_final_recipients(self):
        self.ensure_one()
        signer_emails = set()
        for signer in self.signer_ids:
            email = getattr(signer, 'email', False)
            if email and isinstance(email, str):
                signer_emails.add(email)
        # Si sign_oca tiene CC, adaptar aquí
        return signer_emails

    def initialize_new(self):
        if self.env.context.get('no_sign_mail'):
            return True
        return super().initialize_new() if hasattr(super(), 'initialize_new') else True

    def action_sent(self):
        if self.env.context.get('no_sign_mail'):
            return True
        return super().action_sent() if hasattr(super(), 'action_sent') else True

