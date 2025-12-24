{
    'name': 'Vitaltecuida Sign Partner Documents',
    'version': '18.0.1.0.0',
    'category': 'Document Management',
    'summary': 'Smart button to show signed documents related to contacts',
    'description': """
        This module adds a smart button in the partner form view to show
        all sign requests where the partner is involved as a signer.
    """,
    'author': 'Abraham (Xtendoo)',
    'website': 'https://www.vitaltecuida.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'contacts',
        'sign_oca',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sign_template_wizard_views.xml',
        'views/sign_template_wizard_no_email_views.xml',
        'views/res_partner_views.xml',
        'templates/portal_sign_document_signed.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
