# -*- coding: utf-8 -*-
{
    'name': "Reportes Exógena",

    'summary': """
        reportes de medios magnéticos""",

    'description': """
        reportes de medios magnéticos,
    """,

    'author': "lavish",
    'website': "lavish",
    
    'category': 'Uncategorized',
    'version': '14.2.0.0.5',
    'images': ['static/description/icon.png'],

    'depends': ['base', 'exo_config', 'exo_params'],

    'data': [
        'security/ir.model.access.csv',
        'security/regla_registro_filtro_company.xml',
        'views/vista_ppal.xml',
    ],
}
