# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Management Human Talent',
    'summary': 'HR Mangement Human Talent for todoo',
    'version': '14.0.1.0.2',
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
        'base',
        'hr_payroll', 'hr_contract', 'hr_payroll_extended', 'hr_contract_extended', 'base_address_city', 'analytic', 'hr_payroll_variations',
    ],
    'data': ['security/ir.model.access.csv',
             'security/hr_request_new_security.xml',
             'views/hr_request_new_views.xml',
             'views/inherit_hr_contract_views.xml',
             'views/inherit_hr_employee_views.xml',
             'views/hr_labor_relation_views.xml',
             'views/fields_todoo_view.xml',
             'wizard/salary_increase_wizard_views.xml',
             'views/salary_increase_views.xml',
             'views/analytic_account_views.xml',
             'report/report_history_extend.xml',
             'report/hr_history_extend_report.xml',
             'report/termination_contract_report.xml',
             'report/termination_evaluation_report.xml',
             'data/ir_sequence_data.xml', ],
}
