# -*- coding: utf-8 -*-

{
    'name': 'HR Payroll Account Extended',
    'summary': 'HR Payroll Account Customization for todoo',
    'version': '14.0.1.0.1',
    'category': 'Human Resources',
    'website': 'TL soluciones',
    'author': 'TL soluciones',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'hr_payroll_account',
    ],
    'data': [
        'view/hr_salary_rule_view.xml',
    ],
}
