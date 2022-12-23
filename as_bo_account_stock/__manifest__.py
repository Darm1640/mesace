# -- coding: utf-8 --
{
    'name' : "Asiento de Picking Unificado",
    'version' : "1.0.3",
    'author'  : "Ahorasoft",
    'description': """
Cutomizaciones para generar asiento de movimiento de inventario unificado
===========================

Custom module for MOTOPRO
    """,
    'category' : "account",
    'depends' : [
        "base",
        "account",
        "stock",
        "stock_account",
        ],
    'website': 'http://www.ahorasoft.com',
    'data' : [
            # 'security/ir.model.access.csv',
            'views/as_stock_picking.xml',
            # 'views/as_account_move.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}