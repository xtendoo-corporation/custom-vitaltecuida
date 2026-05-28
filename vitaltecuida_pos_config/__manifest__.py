{
    'name': 'Vitaltecuida POS - Cliente por Defecto',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Permite seleccionar un cliente por defecto en cada caja TPV',
    'description': """
        Este módulo añade la posibilidad de configurar un cliente por defecto
        en cada caja del Punto de Venta (TPV).

        Características:
        - Campo "Cliente por defecto" en la configuración de cada caja TPV
        - El cliente se asigna automáticamente al crear un nuevo pedido
        - El cajero puede cambiarlo manualmente en cualquier momento
        - Específico para Vitaltecuida
    """,
    'author': 'Xtendoo',
    'website': 'https://www.vitaltecuida.com',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'vitaltecuida_pos_config/static/src/js/default_partner.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
