# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'hr_contract_completion',
    'version': '14.0.1.0',
    'author': 'TL soluciones',
    'website': '...',
    'category': 'Human Resources',
    'summary': "Module to manage employee's Contract Completion.",
    'depends': ['base',
                'mail',
                'hr_payroll',
                'hr_payroll_variations',
                ],
    'data': ['data/hr_contract_completion_data.xml',
             'views/hr_contract_completion_view.xml',
             'views/inherited_hr_payslip_view.xml',
             'views/inherited_hr_pv_view.xml',
             'views/inherited_hr_contract_view.xml',
             'views/notice_letter_email.xml',
             'report/notice_letter.xml',
             'wizard/contract_completion_reverse_wizard_view.xml',
             'security/ir.model.access.csv',
             'data/ir.sequence.xml',
             ],
    'installable': True,
    'application': False
}
