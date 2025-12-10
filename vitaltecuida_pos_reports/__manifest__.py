# Copyright 2025 Vitaltecuida
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vitaltecuida - POS Reports',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Informes detallados de sesiones POS con desglose por ticket',
    'author': 'Vitaltecuida',
    'website': 'https://www.vitaltecuida.com',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pos_session_report_wizard_views.xml',
        'reports/pos_session_report_template.xml',
        'reports/pos_session_report.xml',
        'views/pos_session_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

