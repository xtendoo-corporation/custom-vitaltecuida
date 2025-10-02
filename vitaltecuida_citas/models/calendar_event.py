from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    resource_ids = fields.Many2many(
        'appointment.resource',
        'calendar_event_resource_rel',
        'event_id', 'resource_id',
        string='Resources'
    )
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

    @api.depends('resource_ids', 'resource_ids.color')
    def _compute_resource_color(self):
        for event in self:
            # Toma el color hexadecimal del primer recurso asignado
            if event.resource_ids and event.resource_ids[0].color:
                event.resource_color = event.resource_ids[0].color
            else:
                event.resource_color = '#c7c7c7'

    @api.depends('resource_ids', 'resource_ids.color_index')
    def _compute_resource_color_index(self):
        for event in self:
            if event.resource_ids and event.resource_ids[0].color_index:
                event.resource_color_index = event.resource_ids[0].color_index
            else:
                # Asignar un color por defecto que no sea 0 (gris)
                event.resource_color_index = 1  # Rojo por defecto

    def write(self, vals):
        """Recalcula colores cuando se modifican los recursos"""
        result = super().write(vals)
        if 'resource_ids' in vals:
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
