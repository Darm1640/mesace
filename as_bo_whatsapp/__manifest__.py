# -*- coding: utf-8 -*-
{
    'name': "AHORASOFT WHATSAPP GATEWAY 2021",

    'summary': """
        WHATSAPP GATEWAY para chat-api, wablas""",

    'description': """
        WHATSAPP GATEWAY para chat-api, wablas
    """,

    "author": "Ahorasoft",
    "website": "http://www.ahorasoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Integration',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'purchase',
        'account',
        'stock',
        'payment',
        'crm',
        'delivery',
        'point_of_sale',
        'as_configurations',
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/as_config.xml',
        'views/as_whatsapp.xml',
        'views/as_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}