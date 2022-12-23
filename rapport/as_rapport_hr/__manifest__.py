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
    'version': '1.2.4',
    'depends': ['base','hr','hr_contract','survey','web','mail','portal','utm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/as_hr_employee.xml',
        'views/as_survey_cuadrante.xml',
        'views/as_survey_consolidate.xml',
        'views/as_hr_contract.xml',
        'views/as_survey_form.xml',
        'views/as_survey_question.xml',
        'data/as_sequence.xml',
        'views/as_template_image.xml',
        'views/as_formulario_def.xml',
        'views/as_hr_employer.xml',
        'views/as_survey_range.xml',
        'views/as_qweb_login_campos.xml',
        'wizard/as_import_participaciones.xml',
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
