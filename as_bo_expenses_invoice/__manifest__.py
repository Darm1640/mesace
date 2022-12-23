# -*- coding: utf-8 -*-
{
    'name': 'Generar facturas a partir de gastos',
    'version': '1.1.5',
    'category': 'account',
    'author': 'Ahorasoft',
    'summary': 'Generacion de facturas a partir de gastos',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'account',
        'fleet',
        'hr_expense',
        'as_bo_configuration',
        'as_bo_purchase_invoice',
        'as_bo_tesoreria',
        'as_bo_accounting',
    ],
    'data': [
    #    'security/ir.model.access.csv',
        'views/as_hr_expenses.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}