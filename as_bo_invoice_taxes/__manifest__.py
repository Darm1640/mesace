# -*- coding: utf-8 -*-
{
    'name': 'Retenciones y Tipos de Factura Proveedor',
    'version': '1.0.7',
    'category': 'account',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'product',
        'account',
        'purchase',
        'as_bo_accounting',
        'account_tax_python',
        'as_bo_expenses_invoice',
        'as_bo_purchase_invoice',
        'hr_expense',
        'as_bo_tesoreria',

    ],
    'data': [
    #    'security/ir.model.access.csv',
        'data/as_taxes_invoice.xml',
        'views/as_tipo_retencion.xml',
        'views/as_account_move.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}