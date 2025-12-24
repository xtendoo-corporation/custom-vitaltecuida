# pylint: disable=import-error, no-name-in-module
from odoo import models, api, fields, _
import logging

_logger = logging.getLogger(__name__)

class SignOcaRequestSigner(models.Model):
    _inherit = 'sign.oca.request.signer'

    skip_email_validation = fields.Boolean(
        string='Skip Email Validation',
        default=False,
        copy=False,
        help='Campo técnico para omitir validación de email en este firmante'
    )

    @api.constrains('email')
    def _check_signer_email_validity(self):
        _logger.warning("=== _check_signer_email_validity llamado ===")
        _logger.warning(f"Contexto completo: {self.env.context}")
        _logger.warning(f"no_sign_mail en contexto: {self.env.context.get('no_sign_mail')}")
        _logger.warning(f"Partner IDs: {self.mapped('partner_id.id')}")
        _logger.warning(f"Signer emails: {self.mapped('email')}")
        _logger.warning(f"skip_email_validation flags: {self.mapped('skip_email_validation')}")
        if any(sri.skip_email_validation for sri in self):
            _logger.warning("=== SALTANDO validación de email por skip_email_validation flag ===")
            return
        if self.env.context.get('no_sign_mail'):
            _logger.warning("=== SALTANDO validación de email por no_sign_mail ===")
            return
        _logger.warning("=== EJECUTANDO validación de email (NO HAY no_sign_mail) ===")
        return super()._check_signer_email_validity() if hasattr(super(), '_check_signer_email_validity') else True

    @api.constrains('partner_id')
    def _check_partner_email(self):
        if self.env.context.get('no_sign_mail'):
            return
        if hasattr(super(), '_check_partner_email'):
            return super()._check_partner_email()

    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('SignOcaRequestSigner.create llamado')
        _logger.warning(f'Contexto en create: {self.env.context}')
        _logger.warning(f'vals_list: {vals_list}')
        return super().create(vals_list)

    def send_signature_accesses(self):
        if self.env.context.get('no_sign_mail'):
            self.write({'is_mail_sent': False})
            return True
        return super().send_signature_accesses() if hasattr(super(), 'send_signature_accesses') else True
