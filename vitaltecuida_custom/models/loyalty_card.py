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

