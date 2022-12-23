# -*- coding: utf-8 -*-
{
    'name': "RAPPORT customizaciones Encuestas",
      'summary': """
        RAPPORT customizaciones Encuestas""",
    'description': """
        RAPPORT customizaciones Encuestas
    """,
    'author': "ahorasoft",
    'website': "http://www.ahorasoft.com",
    'category': 'hr',
    'version': '1.0.3',
    'depends': ['base','hr','hr_contract','survey','web','as_rapport_hr'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/as_test_config.xml',
        'data/as_data.xml',
      
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/as_template_image.xml',
    # ],
    'installable': True,
    'auto_install': False,
}
