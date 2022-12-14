# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Payroll Extended',
    'summary': 'HR Payroll Customization for todoo',
    'version': '14.0.1.0.4',
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
        'hr_payroll',
        'l10n_latam_base',
        #'l10n_co_dian_data',
        'account_budget',
        'hr_contract_extended',
    ],
    'data': [
        #'views/hr_leaves_generate_view.xml',
        'security/hr_payroll_extended_security.xml',
        'views/hr_payroll_config_parameters_view.xml',
        'views/hr_payroll_config_view.xml',
        'views/inherited_hr_salary_rule_view.xml',
        'views/inherited_res_partner_view.xml',
        'views/inherited_hr_employee_view.xml',
        'views/inherited_resource_calendar_view.xml',
        'views/inherited_hr_leave_type_view.xml',
        'views/inherited_hr_contract_view.xml',
        'data/hr.payroll.structure.categ.csv',
        'security/ir.model.access.csv',
        'views/hr_conf_acumulated_view.xml',
        'views/hr_acumulated_rules_view.xml',
        'views/hr_employee_acumulate_view.xml',
        'views/inherited_hr_leave_allocation.xml',
        'views/inherited_hr_payslip_worked_days.xml',
        'views/inherited_res_bank.xml',
        #'report/payslip_report.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'wizard/hr_payroll_generate_send_wizard_view.xml',
        'wizard/cesantia_found_wizard_view.xml',
        'views/hr_payslip_view.xml',
        'views/generate_send_email_template.xml',
        'wizard/payroll_config_reason_reject_view.xml',
        'wizard/update_leave_details_wizard_view.xml',
        'wizard/reprocess_acumulate_wizard_view.xml',
    ],
}
