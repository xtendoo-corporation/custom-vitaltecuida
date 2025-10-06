{
    'name': 'Vitaltecuida Website - Sistema de Reseñas',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Sistema de reseñas para el sitio web de Vitaltecuida con moderación',
    'description': """
        Este módulo añade un sistema completo de reseñas al sitio web de Vitaltecuida.

        Características:
        - Página pública para enviar reseñas
        - Sistema de moderación (aprobación/rechazo)
        - Visualización solo de reseñas aprobadas
        - Panel de administración para gestionar reseñas
        - Integración con el menú principal del sitio web
        - Diseño responsive y moderno
    """,
    'author': 'Abraham (Xtendoo)',
    'website': 'https://www.vitaltecuida.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'website',
        'mail',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/review_views.xml',
        'templates/review_templates.xml',
        'data/website_pages.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'vitaltecuida_website/static/src/css/review_style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
