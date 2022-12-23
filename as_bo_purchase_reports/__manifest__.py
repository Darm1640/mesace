# -*- coding: utf-8 -*-
{
    'name': 'AhoraSoft REPORTES',
    'version': '1.1.2',
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
        'security/ir.model.access.csv',
        'wizard/as_purchase_report_products.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}