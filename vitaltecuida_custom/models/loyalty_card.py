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
                # Crear mensaje usando plantilla predefinida
                message = self._format_expiry_message(card.partner_id.name, 15, card.expiration_date)

                if message:
                    # Enviar mensaje de WhatsApp usando el sistema nativo de Odoo
                    self._send_whatsapp_message(card.partner_id, message)
                    _logger.info(f"Notificación de expiración enviada a {card.partner_id.name}")
                else:
                    _logger.warning("Error generando mensaje de notificación de expiración")

            except Exception as e:
                _logger.error(f"Error enviando notificación a {card.partner_id.name}: {str(e)}")

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
        Método para enviar mensaje de WhatsApp usando el sistema nativo de Odoo
        """
        try:
            # Usar la plantilla nativa de WhatsApp de Odoo
            if 'whatsapp.template' in self.env:
                whatsapp_template = self.env.ref('vitaltecuida_custom.whatsapp_template_ewallet_expiry', raise_if_not_found=False)

                if whatsapp_template:
                    # Crear el mensaje usando la plantilla nativa
                    # Los parámetros {{1}}, {{2}}, {{3}} serán reemplazados por nombre, días, fecha
                    partner_name = partner.name or 'Cliente'
                    days_remaining = '15'
                    expiration_date = ''

                    # Buscar el monedero del partner para obtener la fecha exacta
                    loyalty_card = self.search([('partner_id', '=', partner.id)], limit=1)
                    if loyalty_card and loyalty_card.expiration_date:
                        expiration_date = loyalty_card.expiration_date.strftime('%d/%m/%Y')

                    # Aquí deberías usar el método nativo de envío de WhatsApp de Odoo
                    # Esto depende de cómo esté configurado tu sistema de WhatsApp
                    _logger.info(f"Usando plantilla WhatsApp nativa para {partner.mobile}")
                    _logger.info(f"Parámetros: {partner_name}, {days_remaining}, {expiration_date}")
                else:
                    _logger.warning("Plantilla de WhatsApp no encontrada, usando mensaje directo")
                    _logger.info(f"Enviando WhatsApp a {partner.mobile}: {message}")
            else:
                # Fallback: registrar en log
                _logger.info(f"WhatsApp no disponible. Mensaje para {partner.mobile}: {message}")

        except Exception as e:
            _logger.error(f"Error en sistema WhatsApp: {str(e)}")

        # Crear una actividad como respaldo independientemente del resultado
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Notificación WhatsApp - Expiración de Monedero',
            'note': f'Mensaje enviado por WhatsApp:\n\n{message}',
            'res_id': partner.id,
            'res_model_id': self.env['ir.model']._get('res.partner').id,
            'user_id': self.env.user.id,
        })

    @api.model
    def _send_birthday_notifications(self):
        """
        Método para enviar felicitaciones de cumpleaños con tarjeta regalo de 10€
        Este método será llamado por el cron job diariamente
        """
        today = datetime.now().date()

        # Buscar partners que cumplan años hoy y tengan móvil
        birthday_partners = self.env['res.partner'].search([
            ('birthdate', '!=', False),
            ('mobile', '!=', False),
            ('is_company', '=', False),  # Solo personas, no empresas
        ])

        partners_to_notify = birthday_partners.filtered(
            lambda p: p.birthdate and p.birthdate.month == today.month and p.birthdate.day == today.day
        )

        for partner in partners_to_notify:
            try:
                # Crear o encontrar el programa de lealtad para tarjetas regalo
                loyalty_program = self._get_or_create_gift_loyalty_program()

                # Crear tarjeta regalo de 10€
                gift_card = self._create_birthday_gift_card(partner, loyalty_program, 10.0)

                if gift_card:
                    # Enviar mensaje de felicitación
                    self._send_birthday_whatsapp_message(partner, gift_card)
                    _logger.info(f"Felicitación de cumpleaños enviada a {partner.name} con tarjeta regalo de 10€")
                else:
                    _logger.warning(f"No se pudo crear tarjeta regalo para {partner.name}")

            except Exception as e:
                _logger.error(f"Error enviando felicitación de cumpleaños a {partner.name}: {str(e)}")

    def _get_or_create_gift_loyalty_program(self):
        """
        Obtiene o crea el programa de lealtad para tarjetas regalo de cumpleaños
        """
        gift_program = self.env['loyalty.program'].search([
            ('name', '=', 'Tarjetas Regalo Cumpleaños Vitaltecuida')
        ], limit=1)

        if not gift_program:
            # Crear programa de lealtad para tarjetas regalo
            gift_program = self.env['loyalty.program'].create({
                'name': 'Tarjetas Regalo Cumpleaños Vitaltecuida',
                'program_type': 'ewallet',
                'trigger': 'auto',
                'active': True,
            })
            _logger.info("Programa de lealtad para tarjetas regalo de cumpleaños creado")

        return gift_program

    def _create_birthday_gift_card(self, partner, loyalty_program, amount):
        """
        Crea una tarjeta regalo de cumpleaños para el partner
        """
        try:
            # Crear la tarjeta de lealtad con saldo
            gift_card = self.create({
                'partner_id': partner.id,
                'program_id': loyalty_program.id,
                'points': amount,  # 10€ como puntos/saldo
                'expiration_date': datetime.now().date() + timedelta(days=365),  # Expira en 1 año
            })

            # Crear actividad en el partner para registro
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'Tarjeta Regalo Cumpleaños - {amount}€',
                'note': f'Tarjeta regalo de {amount}€ creada automáticamente por cumpleaños.\nVálida hasta: {gift_card.expiration_date.strftime("%d/%m/%Y")}',
                'res_id': partner.id,
                'res_model_id': self.env['ir.model']._get('res.partner').id,
                'user_id': self.env.user.id,
            })

            return gift_card

        except Exception as e:
            _logger.error(f"Error creando tarjeta regalo para {partner.name}: {str(e)}")
            return False

    def _send_birthday_whatsapp_message(self, partner, gift_card):
        """
        Envía mensaje de WhatsApp de felicitación de cumpleaños
        """
        try:
            # Usar la plantilla nativa de WhatsApp de cumpleaños
            if 'whatsapp.template' in self.env:
                whatsapp_template = self.env.ref('vitaltecuida_custom.whatsapp_template_birthday_gift', raise_if_not_found=False)

                if whatsapp_template:
                    # El parámetro {{1}} será reemplazado por el nombre del partner
                    partner_name = partner.name or 'Cliente'

                    # Aquí deberías usar el método nativo de envío de WhatsApp de Odoo
                    _logger.info(f"Enviando felicitación de cumpleaños por WhatsApp a {partner.mobile}")
                    _logger.info(f"Parámetro: {partner_name}")

                    # Crear actividad como respaldo
                    self.env['mail.activity'].create({
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': 'WhatsApp Cumpleaños - Tarjeta Regalo Enviada',
                        'note': f'Felicitación de cumpleaños enviada por WhatsApp con tarjeta regalo de 10€.\nTarjeta creada: {gift_card.id}',
                        'res_id': partner.id,
                        'res_model_id': self.env['ir.model']._get('res.partner').id,
                        'user_id': self.env.user.id,
                    })
                else:
                    _logger.warning("Plantilla de WhatsApp de cumpleaños no encontrada")
            else:
                _logger.info(f"WhatsApp no disponible. Felicitación para {partner.mobile}")

        except Exception as e:
            _logger.error(f"Error enviando felicitación WhatsApp a {partner.name}: {str(e)}")
