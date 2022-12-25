# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Contract Extended',
    'version': '14.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'todoo',
    'maintainer': 'todoo',
    'company': 'TL soluciones',
    'website': 'TL soluciones',
    'depends': [
        'hr_contract',
        'hr_recruitment',
        #'hr_payroll_extended',
    ],
    'data': [
        #'data/hr_contract_extended_data.xml',
        'views/inherited_res_company_view.xml',
        'views/inherited_res_users_view.xml',
        'views/hr_marital_status_view.xml',
        'views/hr_center_formation_view.xml',
        'views/hr_contract_reson_change_view.xml',
        #'views/hr_contract_alert_view.xml',
        'views/hr_contract_type_view.xml',
        'views/inherited_hr_employee_view.xml',
        'wizard/reason_change_wizard_view.xml',
        'wizard/hr_contract_generate_send_wizard.xml',
        #'views/inherited_hr_contract_view.xml',
        'security/ir.model.access.csv',
        'views/inherited_hr_job_view.xml',
        'wizard/create_contract_identification_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
