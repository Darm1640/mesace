# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# -*- coding: utf-8 -*-

{
    'name': 'Payroll Income Withholding',
    'version': '14.0.1.0',
    'author': 'TL soluciones',
    'website': '...',
    'category': 'Human Resources',
    'summary': "Module to manage income withholding in payroll of employee",
    'depends': ['base',
                'mail',
                'hr',
                'hr_payroll',
                'hr_payroll_variations',
                'hr_contract_completion',
                ],
    'data': [
        'data/ir_cron_data.xml',
        'views/hr_payroll_income_withholding_view.xml',
        'views/hr_pv_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False
}
