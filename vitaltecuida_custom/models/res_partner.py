from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'


    birthdate = fields.Date(string='Cumpleaños', help='Fecha de cumpleaños del contacto')


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
        Crea una tarjeta regalo de cumpleaños para el partner en loyalty.card
        Si ya tiene una tarjeta regalo de cumpleaños activa, no se crea otra.
        """
        try:
            # Buscar si ya tiene una tarjeta regalo de cumpleaños activa
            existing_card = self.env['loyalty.card'].search([
                ('partner_id', '=', partner.id),
                ('program_id', '=', loyalty_program.id),
                ('expiration_date', '>=', datetime.now().date()),
                ('points', '>=', amount),
            ], limit=1)
            if existing_card:
                _logger.info(f"El partner {partner.name} ya tiene una tarjeta regalo de cumpleaños activa (ID: {existing_card.id})")
                return False

            # Crear la tarjeta de lealtad con saldo en loyalty.card
            gift_card = self.env['loyalty.card'].create({
                'partner_id': partner.id,
                'program_id': loyalty_program.id,
                'points': amount,  # 10€ como puntos/saldo
                'expiration_date': datetime.now().date() + timedelta(days=365),  # Expira en 1 año
            })
            _logger.info(f"Tarjeta regalo de cumpleaños creada para {partner.name} (ID: {gift_card.id})")

            # Crear actividad en el partner para registro
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'Tarjeta Regalo Cumpleaños - {amount}€',
                'note': f'Tarjeta regalo de {amount}€ creada automáticamente por cumpleaños.\nVálida hasta: {gift_card.expiration_date.strftime("%d/%m/%Y")}',
                'res_id': partner.id,
                'res_model_id': self.env['ir.model']._get('res.partner').id,
                'user_id': self.env.user.id,
            })
            _logger.info(f"Actividad registrada en el partner {partner.name} para la tarjeta regalo (ID: {gift_card.id})")

            return gift_card

        except Exception as e:
            _logger.error(f"Error creando tarjeta regalo para {partner.name}: {str(e)}")
            return False


    def _send_birthday_whatsapp_message(self, partner, gift_card):
        """
        Envía mensaje de WhatsApp de felicitación de cumpleaños usando plantilla avanzada y fallback
        """
        try:
            whatsapp_account = self._get_whatsapp_account()
            phone_number = partner.mobile
            template = getattr(self, 'whatsapp_template_id', False)

            # Si no hay template configurado, buscar uno predeterminado para cumpleaños
            if not template:
                _logger.info("No hay template configurado en el partner, buscando uno predeterminado de cumpleaños")
                # Buscar plantilla específica de cumpleaños
                template_names = ['Felicitación Cumpleaños Vitaltecuida', 'Cumpleaños Vitaltecuida', 'Cumpleaños']
                for name in template_names:
                    template = self.env['whatsapp.template'].search([
                        ('name', '=', name),
                        ('model', '=', 'res.partner')
                    ], limit=1)
                    if template:
                        _logger.info(f"Encontrada plantilla de cumpleaños por nombre: {name}")
                        break
                if not template:
                    _logger.warning("No se encontraron plantillas de cumpleaños por nombre, buscando cualquier plantilla para res.partner")
                    template = self.env['whatsapp.template'].search([
                        ('model', '=', 'res.partner')
                    ], limit=1)
            if not template:
                _logger.error("No se encontró ninguna plantilla de WhatsApp de cumpleaños para res.partner")
                return False

            _logger.info(f"Usando plantilla de cumpleaños: {template.name} [ID: {template.id}] para el partner {partner.name}")

            # Preparar contexto de renderizado
            ctx = {
                'partner_name': partner.name,
                'gift_card_id': gift_card.id,
                'gift_card_amount': gift_card.points,
                'gift_card_expiration': gift_card.expiration_date.strftime('%d/%m/%Y'),
            }
            _logger.info(f"Contexto de renderizado: {ctx}")

            # Crear compositor de WhatsApp
            composer_values = {
                'wa_template_id': template.id,
                'res_model': 'res.partner',
                'res_ids': partner.id,
                'phone': phone_number,
            }
            composer = self.env['whatsapp.composer'].sudo().create(composer_values)
            _logger.info(f"Compositor creado con ID: {composer.id}")

            # Cargar la plantilla
            try:
                composer.onchange_template_id()
                _logger.info("Plantilla cargada correctamente en el compositor")
            except Exception as e:
                _logger.warning(f"Error al cargar la plantilla en el compositor: {e}")

            # Enviar el mensaje utilizando el método nativo
            try:
                result = composer.sudo().action_send_whatsapp_template()
                _logger.info(f"Mensaje enviado: {result}")
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'WhatsApp Cumpleaños - Tarjeta Regalo Enviada',
                    'note': f'Felicitación de cumpleaños enviada por WhatsApp con tarjeta regalo de 10€.\nTarjeta creada: {gift_card.id}',
                    'res_id': partner.id,
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'user_id': self.env.user.id,
                })
                _logger.info(f"Actividad registrada en el partner {partner.name} para el WhatsApp de cumpleaños")
                return True
            except Exception as e:
                _logger.error(f"Error al enviar el mensaje de WhatsApp: {e}", exc_info=True)
                # Fallback: enviar mensaje básico por API REST
                message_body = self._get_default_whatsapp_message(partner, gift_card)
                return self._send_fallback_message(whatsapp_account, phone_number, message_body, partner)

        except Exception as e:
            _logger.error(f"Error enviando felicitación WhatsApp a {partner.name}: {str(e)}", exc_info=True)
            return False

    def _get_whatsapp_account(self):
        """Obtiene una cuenta de WhatsApp disponible"""
        WhatsAppAccount = self.env['whatsapp.account']
        account = WhatsAppAccount.search([('active', '=', True)], limit=1)
        if not account:
            account = WhatsAppAccount.search([], limit=1)
        return account

    def _get_default_whatsapp_message(self, partner, gift_card):
        """Genera el mensaje básico de cumpleaños para fallback"""
        return f"¡Feliz cumpleaños {partner.name}! Te regalamos una tarjeta de {gift_card.points}€ válida hasta {gift_card.expiration_date.strftime('%d/%m/%Y')}. ¡Disfrútala!"

    def _send_fallback_message(self, whatsapp_account, phone_number, message_body, partner):
        """Método simplificado para enviar mensaje como fallback cuando falla el compositor"""
        try:
            import requests
            import json
            if not whatsapp_account or not whatsapp_account.token or not whatsapp_account.phone_uid:
                _logger.error("Falta configuración de WhatsApp")
                return False
            if not phone_number:
                _logger.error("No se proporcionó número de teléfono")
                return False
            clean_phone = phone_number.lstrip('+')
            url = f"https://graph.facebook.com/v18.0/{whatsapp_account.phone_uid}/messages"
            headers = {
                'Authorization': f'Bearer {whatsapp_account.token}',
                'Content-Type': 'application/json'
            }
            data = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "body": message_body
                }
            }
            _logger.info(f"Enviando vía API REST fallback a {clean_phone}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                _logger.info(f"Mensaje de fallback enviado exitosamente")
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'WhatsApp Cumpleaños - Tarjeta Regalo Enviada (Fallback)',
                    'note': f'Felicitación de cumpleaños enviada por WhatsApp (fallback) con tarjeta regalo de 10€.\nTarjeta creada: {gift_card.id}',
                    'res_id': partner.id,
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'user_id': self.env.user.id,
                })
                _logger.info(f"Actividad registrada en el partner {partner.name} para el WhatsApp de cumpleaños (fallback)")
                return True
            else:
                _logger.error(f"Error en API REST fallback: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            _logger.error(f"Error en fallback: {e}", exc_info=True)
            return False
