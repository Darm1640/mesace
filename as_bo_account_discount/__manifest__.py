# -*- coding: utf-8 -*-
{
    'name': 'Descuentos en compra y Venta',
    'version': '1.0.9',
    'category': 'purchase',
    'author': 'Ahorasoft',
    'summary': 'Asientos de descuento en compras y ventas',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'account',
        'base_setup',
        'stock',
        'as_bo_accounting',
       
    ],
    'data': [
        # 'security/as_group_view.xml',
        'security/ir.model.access.csv',
        'views/as_account_move.xml',
        'views/global_discount_views.xml',
       
        
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}