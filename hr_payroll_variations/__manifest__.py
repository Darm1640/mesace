# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'hr_payroll_variations',
    'version': '14.0.1.02',
    'author': 'TL-Soluction',
    'website': '',
    'category': 'Human Resources',
    'summary': "Module to manage employee's payroll variants. i.e: ",
    'depends': ['base',
                'mail',
                'hr',
                'hr_holidays',
                'recruitment_reason',
                'hr_contract_extended',
                'hr_payroll_extended',
                ],
    'data': [
        'security/hr_pv_security.xml',
        'data/calendar_data.xml',
        'data/hr_pv_type.xml',
        'data/hr_pv_type_subtype.xml',
        'data/hr_pv_event.xml',
        'data/ir.sequence.xml',
        'wizard/create_pv_wizard_view.xml',
        'wizard/cancel_assignment_wizard.xml',
        'views/hr_leave_code_view.xml',
        'views/hr_leave_view.xml',
        'views/inherited_hr_contract_view.xml',
        'views/hr_employee_view.xml',
        'views/inherited_hr_leaves_view.xml',
        'views/inherited_hr_payslip_view.xml',
        'views/inherit_hr_job_view.xml',
        'views/inherited_resource_calendar_view.xml',
        
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'wizard/pv_create_contact_view.xml',
        'wizard/pv_create_employee_view.xml',
        'wizard/pv_create_contract_view.xml',
        'views/hr_pv_view.xml',
        'wizard/pv_reject_wizard_view.xml',
        'wizard/pv_cancel_wizard_view.xml',
        'security/groups.xml',
        'views/hr_assignment_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'external_dependencies': {
       # 'python': ['ip2geotools'],
    }
}
