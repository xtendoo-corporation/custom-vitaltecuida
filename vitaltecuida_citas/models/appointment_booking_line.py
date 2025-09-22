
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class AppointmentBookingLineInherit(models.Model):
    _inherit = "appointment.booking.line"

    @api.constrains('appointment_resource_id', 'appointment_type_id')
    def _check_resources_match_appointment_type(self):
        for appointment_type, lines in self.grouped('appointment_type_id').items():
            if not appointment_type:
                continue  # Omitir si es False o None
            non_compatible_resources = lines.appointment_resource_id - appointment_type.resource_ids
            if non_compatible_resources:
                raise ValidationError(_('"%(resource_name_list)s" no se puede usar para "%(appointment_type_name)s"',
                                        appointment_type_name=appointment_type.name,
                                        resource_name_list=', '.join(non_compatible_resources.mapped('name'))))
