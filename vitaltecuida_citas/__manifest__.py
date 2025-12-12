# -*- coding: utf-8 -*-
{
    'name': 'VitalTeCuida Citas',
    'summary': 'Extiende las citas para asignar recursos (empleados) y visualizarlos en el calendario.',
    'description': 'Permite asignar empleados como recursos a las citas y visualizarlos en la vista calendario.',
    'author': 'Abraham (Xtendoo)',
    'website': '',
    'category': 'Services/Appointment',
    'version': '18.0.1.0.0',
    'depends': ['appointment', 'hr', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'views/appointment_resource_views.xml',
        'views/calendar_event_wizard_views.xml',
        'views/appointment_resource_calendar.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
