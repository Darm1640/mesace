# -*- coding: utf-8 -*-
{
    'name': 'Retorno de Stock Inventario',
    'version': '1.0.1',
    'category': 'Stock',
    'author': 'Ahorasoft',
    'summary': 'Retorno de stock inventario para Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'stock',
        'sale',
        'product',
        'as_bo_account_automatic',
    ],
    'data': [
       'security/ir.model.access.csv',
       'views/as_stock_account_action.xml',
       'views/as_stock_inventory.xml',
       
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}