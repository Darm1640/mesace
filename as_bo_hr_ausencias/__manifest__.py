# -*- coding: utf-8 -*-
{
    'name': 'Generador de Ausencias en nomina',
    'version': '1.1.0',
    'category': 'hr',
    'author': 'Ahorasoft',
    'summary': 'Ausencias en nomina',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'hr',
        'hr_payroll',
        'hr_holidays',
      
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'report/as_reporte_vacaciones_pdf.xml',
        'views/report/as_reporte_solicitud_permisos.xml',
        'views/report/as_reporte_solicitud_vacaciones.xml',
        'views/as_hr_leave_type.xml',
        'views/as_hr_leave.xml',
        'views/as_hr_periodo.xml',
        'views/as_report_format.xml',
        'wizard/as_reporte_vacaciones.xml',
      
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}