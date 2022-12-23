# -*- coding: utf-8 -*-
{
    'name': 'AhoraSoft REPORTES de inventario',
    'version': '1.0.5',
    'category': 'Stock',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'stock',
        'sale',
        'product',
        "purchase_stock",
        'sale_management',
        'report_xlsx',
        'purchase',
    ],
    'data': [
        
        'views/as_stock_picking_report.xml',
        'views/report/as_stock_picking_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}