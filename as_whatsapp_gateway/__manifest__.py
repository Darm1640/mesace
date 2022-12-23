# -*- coding: utf-8 -*-
{
    'name': "Integración con Whatsapp",

    'summary': """
        WHATSAPP GATEWAY para chat-api, wablas""",

    'description': """
        WHATSAPP GATEWAY para chat-api, wablas
    """,

    "author": "Ahorasoft",
    "website": "https://www.ahorasoft.com/",

    'category': 'Integration',
    'version': '1.0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail'
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/as_config.xml',
        'views/as_whatsapp.xml',
        'views/as_menu.xml',
        'views/as_res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}