{
    "name": "Vitaltecuida Bonos",
    "version": "18.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Bonos por usos para producto, contacto y punto de venta",
    "author": "Abraham (Xtendoo)",
    "website": "https://www.xtendoo.es",
    "license": "AGPL-3",
    "depends": [
        "product",
        "contacts",
        "point_of_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/bono_balance_views.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "vitaltecuida_bonos/static/src/scss/bono_backend.scss",
        ],
        "point_of_sale._assets_pos": [
            "vitaltecuida_bonos/static/src/app/control_buttons/use_bono_button.js",
            "vitaltecuida_bonos/static/src/app/control_buttons/use_bono_button.xml",
            "vitaltecuida_bonos/static/src/app/models/pos_order.js",
            "vitaltecuida_bonos/static/src/app/models/pos_order_line.js",
            "vitaltecuida_bonos/static/src/app/store/pos_store.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
