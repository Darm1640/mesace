# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Payroll Employee Extended',
    'summary': 'HR Payroll Employee Extended, manage Laboral Certification for todoo',
    'version': '14.0.1.1.0',
    'category': 'Human Resources',
    'website': 'TL soluciones',
    'author': 'todoo',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'hr_payroll',
        'hr_payroll_variations',
        'hr_management_human_talent',
        'hr_thomas',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/hr_contract_report.xml',
        'report/report_laboral_certification.xml',
        'views/inherited_hr_employee_view.xml',
        'views/inherited_res_company_view.xml',
        'wizard/hr_employee_generate_send_wizard_view.xml',
    ],
}
