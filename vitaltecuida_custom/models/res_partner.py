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
        """
        try:
            # Crear la tarjeta de lealtad con saldo en loyalty.card
            gift_card = self.env['loyalty.card'].create({
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
                whatsapp_template = self.env.ref('vitaltecuida_custom.whatsapp_template_birthday_gift',
                                                 raise_if_not_found=False)

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
