# models/appointment_resource.py
from odoo import models, fields, api

class AppointmentResource(models.Model):
    _inherit = 'appointment.resource'

    color = fields.Char(string='Color')
    color_index = fields.Integer(string='Color Index')
    color_preview = fields.Char(
        string='Color Preview',
        compute='_compute_color_preview',
        help='Muestra el nombre del color correspondiente al índice'
    )

    @api.depends('color_index')
    def _compute_color_preview(self):
        # Mapeo de índices a nombres de colores
        color_names = {
            0: 'Sin color / Gris',
            1: 'Rojo (#FF0000)',
            2: 'Naranja (#FF8800)',
            3: 'Amarillo (#FFFF00)',
            4: 'Verde claro (#88FF00)',
            5: 'Verde (#00FF00)',
            6: 'Cyan (#00FF88)',
            7: 'Azul claro (#0088FF)',
            8: 'Azul (#0000FF)',
            9: 'Violeta (#8800FF)',
            10: 'Magenta (#FF00FF)',
            11: 'Rosa (#FF0088)'
        }

        for resource in self:
            index = resource.color_index or 0
            resource.color_preview = color_names.get(index, f'Índice {index} (personalizado)')
