# -*- coding: utf-8 -*-
{
    'name': 'Fecha Editable en Movimiento de Inventario',
    'version': '1.0.1',
    'category': 'Stock',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'stock',
        'sale',
    ],
    'data': [
    #    'security/ir.model.access.csv',
        'views/as_stock_picking.xml',
       
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}