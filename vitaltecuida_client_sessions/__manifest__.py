{
    'name': 'Vitaltecuida Client Sessions',
    'version': '18.0.1.0.0',
    'category': 'Customer Relationship Management',
    'summary': 'Gestión de sesiones de clientes con smart button en contactos',
    'description': """
        Este módulo permite gestionar sesiones de clientes desde el formulario de contactos.

        Características:
        * Smart button en contactos para acceder a sesiones
        * Modelo de sesiones con campos: nombre, fecha, observaciones y extras
        * Vistas de lista y formulario para gestionar sesiones
    """,
    'author': 'Abraham (Xtendoo)',
    'website': '',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/client_sessions_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

