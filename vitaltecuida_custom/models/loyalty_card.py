from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribir el método create para establecer automáticamente
        la fecha de expiración a 1 año después de la creación
        """
        for vals in vals_list:
            # Solo establecer expiration_date si no se ha proporcionado ya
            if 'expiration_date' not in vals or not vals.get('expiration_date'):
                # Establecer fecha de expiración a 1 año desde hoy
                expiration_date = datetime.now().date() + timedelta(days=365)
                vals['expiration_date'] = expiration_date

        return super().create(vals_list)

    @api.model
    def default_get(self, fields_list):
        """
        Establecer valores por defecto, incluyendo la fecha de expiración
        """
        defaults = super().default_get(fields_list)

        # Si expiration_date está en la lista de campos y no tiene valor
        if 'expiration_date' in fields_list and 'expiration_date' not in defaults:
            # Establecer fecha de expiración a 1 año desde hoy
            expiration_date = datetime.now().date() + timedelta(days=365)
            defaults['expiration_date'] = expiration_date

        return defaults

    @api.model
    def _send_expiry_notifications(self):
        """
        Método para enviar notificaciones de WhatsApp 15 días antes de la expiración
        Este método será llamado por el cron job diariamente
        """
        # Calcular la fecha de dentro de 15 días
        notification_date = datetime.now().date() + timedelta(days=15)

        # Buscar monederos que expiren exactamente en 15 días
        cards_to_notify = self.search([
            ('expiration_date', '=', notification_date),
            ('partner_id', '!=', False),
            ('partner_id.mobile', '!=', False),
        ])

        for card in cards_to_notify:
            try:
                _logger.info(f"Procesando tarjeta ID: {card.id}, partner: {card.partner_id.name}, expiración: {card.expiration_date}, móvil: {card.partner_id.mobile}")
                # Crear mensaje usando plantilla predefinida
                message = self._format_expiry_message(card.partner_id.name, 15, card.expiration_date)

                if message:
                    _logger.info(f"Mensaje generado para {card.partner_id.name}: {message}")
                    # Enviar mensaje de WhatsApp usando el sistema nativo de Odoo
                    self._send_whatsapp_message(card.partner_id, message)
                    _logger.info(f"Notificación de expiración enviada a {card.partner_id.name} (ID tarjeta: {card.id})")
                else:
                    _logger.warning(f"Error generando mensaje de notificación de expiración para {card.partner_id.name} (ID tarjeta: {card.id})")

            except Exception as e:
                _logger.error(f"Error enviando notificación a {card.partner_id.name} (ID tarjeta: {card.id}): {str(e)}")
        _logger.info(f"Total de tarjetas procesadas para notificación de expiración: {len(cards_to_notify)}")

    def _format_expiry_message(self, partner_name, days_remaining, expiration_date):
        """
        Formatea el mensaje de expiración con plantilla predefinida
        """
        message = f"""🔔 *Vitaltecuida - Aviso Importante*

Hola {partner_name or 'Cliente'},

Tu monedero electrónico está próximo a vencer.

⏰ *Días restantes:* {days_remaining} días
📅 *Fecha de expiración:* {expiration_date.strftime('%d/%m/%Y') if expiration_date else ''}

💡 *¿Qué puedes hacer?*
• Usa tu saldo antes de la fecha de vencimiento
• Contacta con nosotros para renovar tu monedero
• Visita nuestros centros Vitaltecuida

📞 *¿Necesitas ayuda?*
Contáctanos al WhatsApp o visita www.vitaltecuida.com

¡Gracias por confiar en Vitaltecuida! 💚"""

        return message

    def _send_whatsapp_message(self, partner, message):
        """
        Método para enviar mensaje de WhatsApp usando la plantilla 'Vitaltecuida - Aviso Expiración Monedero' con whatsapp.composer
        """
        try:
            # Mostrar en log todos los nombres de las plantillas disponibles
            all_templates = self.env['whatsapp.template'].search([])
            template_names = [t.name for t in all_templates]
            _logger.info(f"Nombres de todas las plantillas WhatsApp: {template_names}")

            # Buscar y usar solo la plantilla exacta de expiración de monedero
            whatsapp_template = self.env['whatsapp.template'].search([
                ('name', '=', 'Vitaltecuida - Aviso Expiración Monedero'),
                ('model', '=', 'res.partner')
            ], limit=1)
            if not whatsapp_template:
                _logger.error("No se encontró la plantilla 'Vitaltecuida - Aviso Expiración Monedero' para res.partner. Abortando envío.")
                _logger.info(f"Enviando WhatsApp a {partner.mobile}: {message}")
            else:
                partner_name = partner.name or 'Cliente'
                days_remaining = '15'
                expiration_date = ''
                loyalty_card = self.search([('partner_id', '=', partner.id)], limit=1)
                if loyalty_card and loyalty_card.expiration_date:
                    expiration_date = loyalty_card.expiration_date.strftime('%d/%m/%Y')
                _logger.info(f"Usando plantilla WhatsApp: {whatsapp_template.name} para {partner.mobile}")
                _logger.info(f"Parámetros: {partner_name}, {days_remaining}, {expiration_date}")
                # Envío real con whatsapp.composer
                composer_values = {
                    'wa_template_id': whatsapp_template.id,
                    'res_model': 'res.partner',
                    'res_ids': partner.id,
                    'phone': partner.mobile,
                }
                composer = self.env['whatsapp.composer'].sudo().create(composer_values)
                _logger.info(f"Compositor WhatsApp creado con ID: {composer.id}")
                try:
                    composer.onchange_template_id()
                    _logger.info("Plantilla cargada correctamente en el compositor")
                except Exception as e:
                    _logger.warning(f"Error al cargar la plantilla en el compositor: {e}")
                try:
                    result = composer.sudo().action_send_whatsapp_template()
                    _logger.info(f"Mensaje de WhatsApp enviado: {result}")
                except Exception as e:
                    _logger.error(f"Error enviando mensaje de WhatsApp: {e}", exc_info=True)
        except Exception as e:
            _logger.error(f"Error en sistema WhatsApp: {str(e)}")
