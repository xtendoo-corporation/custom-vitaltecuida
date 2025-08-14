{
    'name': 'Vitaltecuida Custom - Monedero Electrónico',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Establece automáticamente fecha de expiración de monederos electrónicos a 1 año y notifica por WhatsApp',
    'description': """
        Este módulo automáticamente establece la fecha de expiración de los
        monederos electrónicos (loyalty cards) a 1 año después de su creación.

        Características:
        - Fecha de expiración automática al crear un monedero
        - Compatible con el sistema de loyalty cards de Odoo
        - Notificaciones por WhatsApp 15 días antes de la expiración
        - Integración con el sistema nativo de WhatsApp de Odoo
        - Específico para Vitaltecuida
    """,
    'author': 'Vitaltecuida',
    'website': 'https://www.vitaltecuida.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'loyalty',
        'mail',
        'contacts',
    ],
    'data': [
        'data/whatsapp_template_data.xml',
        'data/cron_data.xml',
        'views/res_partner_form_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
