# -*- coding: utf-8 -*-
{
    'name' : "Ahorasoft NUCLEO - Compras",
    'version': '1.0.3',
    'category': 'purchase',
    'author': 'AhoraSoft',
    'summary': 'Customized purchase Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends' : ['base','purchase','account',"purchase_stock"],
    'data': [
        #  'security/ir.model.access.csv',
        #  'wizard/as_import_moves.xml',
         'security/as_group_view.xml',
         'views/as_account_move.xml',
         'views/as_purchase.xml',
        #  'views/as_purchase_order.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

