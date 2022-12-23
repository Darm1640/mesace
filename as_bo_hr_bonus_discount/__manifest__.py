# -*- coding: utf-8 -*-
{
    'name': 'Generador de Descuentos y Abonos en nomina',
    'version': '1.1.5',
    'category': 'hr',
    'author': 'Ahorasoft',
    'summary': 'Descuentos y Abonos en nomina',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'hr',
        'hr_payroll',
        'as_bo_hr',
        'as_bo_tesoreria',
      
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/bonus_sequence.xml',
        'data/as_payroll_data.xml',
        'views/employee_bonus_view.xml',
        'views/employee_bonus_reports.xml',
        'views/as_hr_payslip_input.xml',
        'views/as_hr_employee.xml',
        'views/report/as_report_quincena_pdf.xml',
        'wizard/as_asignar_bonus_discount.xml',
        'wizard/as_hr_employes.xml',
        'wizard/as_payment_bonus.xml',
      
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}