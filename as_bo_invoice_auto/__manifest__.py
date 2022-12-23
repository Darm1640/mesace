# -*- coding: utf-8 -*-
{
    'name': 'Autocompletar venta en factura',
    'version': '1.0.5',
    'category': 'sale',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'sale',
        'account',
        'base_setup',
        'as_bo_tesoreria',
        'as_bo_invoice_client',
    ],
    'data': [
       'security/ir.model.access.csv',
        'report/as_sale_invoice.xml',
        'views/as_account_move.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}