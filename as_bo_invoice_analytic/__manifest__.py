# -*- coding: utf-8 -*-
{
    'name': 'Autocompletar venta en factura',
    'version': '1.0.1',
    'category': 'sale',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'sale',
        'account',
        'base_setup',
        'analytic',
    ],
    'data': [
       'security/ir.model.access.csv',
        'wizard/as_analytic_update.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}