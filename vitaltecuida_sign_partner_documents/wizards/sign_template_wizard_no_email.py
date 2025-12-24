# pylint: disable=import-error, no-name-in-module
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
        'sign.oca.template',
        string='Plantilla de Firma',
        required=True,
        help='Seleccione la plantilla de firma a utilizar'
    )

    def action_sign_now(self):
        """Ejecuta la acción de firmar ahora con la plantilla y partner seleccionados (sin requerir email)"""
        self.ensure_one()
        _logger.warning('INICIO action_sign_now')
        if not self.sign_template_id:
            _logger.error('No se seleccionó plantilla de firma')
            raise UserError(_('Debe seleccionar una plantilla de firma.'))
        sign_template = self.sign_template_id
        _logger.info(f'Plantilla seleccionada: {sign_template.display_name} (ID: {sign_template.id})')
        # Obtener el primer rol de los items de la plantilla
        first_item_with_role = next((item for item in sign_template.item_ids if item.role_id), None)
        if not first_item_with_role:
            _logger.error('No se encontró ningún rol en los items de la plantilla')
            raise UserError(_('No se pudo determinar el rol de firma en la plantilla. Por favor, configure la plantilla correctamente.'))
        signer_role = first_item_with_role.role_id
        _logger.info(f'Rol seleccionado: {signer_role.name} (ID: {signer_role.id})')
        ctx = dict(self.env.context or {})
        ctx.update({'no_sign_mail': True})
        # Asegurarse de que el PDF de la plantilla se pase a la solicitud
        if not sign_template.data:
            _logger.error('La plantilla no tiene PDF adjunto (campo data vacío)')
        else:
            _logger.info(f'La plantilla tiene PDF adjunto (bytes: {len(sign_template.data)})')
        vals = {
            'template_id': sign_template.id,
            'signer_ids': [Command.create({
                'partner_id': self.partner_id.id,
                'role_id': signer_role.id,
            })],
            'name': sign_template.name,
            'filename': sign_template.filename,
            'data': sign_template.data,  # CLAVE: pasar el PDF
            'signatory_data': sign_template._get_signatory_data(),  # CLAVE: poblar campos de firma
        }
        sign_request = self.env['sign.oca.request'].with_context(**ctx).create(vals)
        _logger.warning(f'signatory_data generado: {sign_request.signatory_data}')
        signer = sign_request.signer_ids and sign_request.signer_ids[0] or False
        if not signer:
            _logger.error('No se pudo crear el firmante')
            raise UserError(_('No se pudo crear el firmante.'))
        signer._portal_ensure_token()
        # Pasar contexto especial para ocultar mensaje de email final
        sign_request.action_send(sign_now=True)
        return {
            'type': 'ir.actions.act_url',
            'url': signer.access_url + '?no_email_thanks=1',
            'target': 'new',
        }
