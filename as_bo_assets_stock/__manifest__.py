# -*- coding: utf-8 -*-
{
    'name': 'Administración de Activos fijos en Inventario',
    'version': '1.0.2',
    'category': 'Stock',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'stock',
        'product',
        'om_account_asset',
        'as_bo_assets',
     
    ],
    'data': [
       'security/ir.model.access.csv',
        'views/as_stock_picking.xml',
        'views/as_account_asset.xml',
        'views/account_asset_category.xml',
      
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}