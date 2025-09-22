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
        "views/view_calendar_event_form_quick_inherit.xml",
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'vitaltecuida_citas/static/src/js/attendee_calendar_patch.js',
    #     ],
    # },
    # 'qweb': [
    #     'static/src/views/attendee_calendar_common_renderer_inherit.xml',
    # ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

