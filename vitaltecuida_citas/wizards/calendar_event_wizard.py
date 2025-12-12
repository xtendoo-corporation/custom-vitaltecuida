# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class CalendarEventWizard(models.TransientModel):
    _name = 'calendar.event.wizard'
    _description = 'Asistente para Crear Citas'

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        help='Seleccione el cliente para la cita'
    )
    appointment_type_id = fields.Many2one(
        'appointment.type',
        string='Tipo de Cita',
        help='Seleccione el tipo de cita'
    )
    name = fields.Char(
        string='Nombre de la Cita',
        required=True,
        help='Ingrese un nombre descriptivo para la cita'
    )
    start = fields.Datetime(
        string='Fecha y Hora Inicio',
        required=True,
        default=lambda self: self._default_start()
    )
    stop = fields.Datetime(
        string='Fecha y Hora Fin',
        required=True,
        compute='_compute_stop',
        store=True,
        readonly=False
    )
    duration = fields.Float(
        string='Duración (horas)',
        default=1.0,
        help='Duración de la cita en horas'
    )
    resource_ids = fields.Many2many(
        'appointment.resource',
        'wizard_event_resource_rel',
        'wizard_id', 'resource_id',
        string='Recursos Asignados',
        required=True,
        help='Seleccione uno o más recursos para asignar a esta cita'
    )
    description = fields.Html(
        string='Descripción'
    )

    def _default_start(self):
        """Obtener fecha de inicio del contexto o usar la actual"""
        start_date = self.env.context.get('default_start')
        if start_date:
            if isinstance(start_date, str):
                return fields.Datetime.from_string(start_date)
            return start_date
        return fields.Datetime.now()

    @api.depends('start', 'duration')
    def _compute_stop(self):
        for wizard in self:
            if wizard.start and wizard.duration:
                wizard.stop = wizard.start + timedelta(hours=wizard.duration)
            elif wizard.start:
                wizard.stop = wizard.start + timedelta(hours=1)

    @api.onchange('start')
    def _onchange_start(self):
        """Actualizar stop cuando cambia start"""
        if self.start and self.duration:
            self.stop = self.start + timedelta(hours=self.duration)

    @api.onchange('duration')
    def _onchange_duration(self):
        """Actualizar stop cuando cambia la duración"""
        if self.start and self.duration:
            self.stop = self.start + timedelta(hours=self.duration)

    @api.onchange('appointment_type_id')
    def _onchange_appointment_type(self):
        """Actualizar duración basada en el tipo de cita si está configurado"""
        if self.appointment_type_id and hasattr(self.appointment_type_id, 'appointment_duration'):
            # Si el tipo de cita tiene duración configurada, usarla
            if self.appointment_type_id.appointment_duration:
                self.duration = self.appointment_type_id.appointment_duration

    def action_create_event(self):
        """Crear el evento de calendario con los datos del wizard"""
        self.ensure_one()

        # Preparar valores para el evento
        event_vals = {
            'name': self.name,
            'start': self.start,
            'stop': self.stop,
            'partner_ids': [(4, self.partner_id.id)],
            'description': self.description,
        }

        # Añadir tipo de cita si existe
        if self.appointment_type_id:
            event_vals['appointment_type_id'] = self.appointment_type_id.id

        # Crear el evento primero
        event = self.env['calendar.event'].create(event_vals)

        # Crear booking lines para cada recurso seleccionado
        if self.resource_ids:
            booking_lines = []
            for resource in self.resource_ids:
                booking_lines.append((0, 0, {
                    'appointment_resource_id': resource.id,
                    'calendar_event_id': event.id,
                    'capacity_reserved': 1,
                    'capacity_used': 1,
                }))
            event.write({'booking_line_ids': booking_lines})

        # Cerrar el wizard y recargar la vista
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_cancel(self):
        """Cancelar y cerrar el wizard"""
        return {'type': 'ir.actions.act_window_close'}

