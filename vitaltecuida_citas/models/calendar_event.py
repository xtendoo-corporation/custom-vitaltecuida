from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # Campo many2many para los recursos asignados (computed)
    resource_ids = fields.Many2many(
        'appointment.resource',
        compute='_compute_resource_ids',
        inverse='_inverse_resource_ids',
        string='Recursos Asignados',
        store=False
    )

    # El campo appointment_type_id ya existe en el modelo base
    # Solo extendemos con los campos de color para recursos
    resource_color = fields.Char(
        string='Resource Color',
        compute='_compute_resource_color',
        store=True
    )
    resource_color_index = fields.Integer(
        string='Resource Color Index',
        compute='_compute_resource_color_index',
        store=True
    )

    @api.depends('booking_line_ids', 'booking_line_ids.appointment_resource_id')
    def _compute_resource_ids(self):
        """Obtener recursos desde booking_line_ids"""
        for event in self:
            event.resource_ids = event.booking_line_ids.mapped('appointment_resource_id')

    def _inverse_resource_ids(self):
        """Actualizar booking_line_ids cuando se modifican los recursos"""
        for event in self:
            # Eliminar booking lines existentes
            event.booking_line_ids.unlink()

            # Crear nuevos booking lines para cada recurso
            if event.resource_ids:
                booking_lines = []
                for resource in event.resource_ids:
                    booking_lines.append((0, 0, {
                        'appointment_resource_id': resource.id,
                        'calendar_event_id': event.id,
                        'capacity_reserved': 1,
                        'capacity_used': 1,
                    }))
                event.booking_line_ids = booking_lines

    @api.depends('appointment_resource_ids', 'appointment_resource_ids.color')
    def _compute_resource_color(self):
        for event in self:
            # Toma el color hexadecimal del primer recurso asignado
            if event.appointment_resource_ids and event.appointment_resource_ids[0].color:
                event.resource_color = event.appointment_resource_ids[0].color
            else:
                event.resource_color = '#c7c7c7'

    @api.depends('appointment_resource_ids', 'appointment_resource_ids.color_index')
    def _compute_resource_color_index(self):
        for event in self:
            if event.appointment_resource_ids and event.appointment_resource_ids[0].color_index:
                event.resource_color_index = event.appointment_resource_ids[0].color_index
            else:
                # Asignar un color por defecto que no sea 0 (gris)
                event.resource_color_index = 1  # Rojo por defecto

    def write(self, vals):
        """Recalcula colores cuando se modifican los recursos"""
        result = super().write(vals)
        if 'booking_line_ids' in vals or 'appointment_resource_ids' in vals:
            self._compute_resource_color_index()
            self._compute_resource_color()
        return result

    @api.model
    def _ensure_resource_colors(self):
        """Método para asegurar que todos los recursos tengan colores"""
        resources = self.env['appointment.resource'].search([])
        color_index = 1
        for resource in resources:
            if not resource.color_index:
                resource.color_index = color_index
                color_index = (color_index % 11) + 1  # Ciclar entre 1-11
            if not resource.color:
                # Colores hexadecimales por defecto
                colors = ['#ff0000', '#ff8800', '#ffff00', '#88ff00', '#00ff00',
                         '#00ff88', '#0088ff', '#0000ff', '#8800ff', '#ff00ff', '#ff0088']
                resource.color = colors[(resource.color_index - 1) % len(colors)]

    @api.model
    def open_appointment_wizard(self):
        """Abrir wizard para crear cita desde calendario"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva Cita',
            'res_model': 'calendar.event.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context),
        }

