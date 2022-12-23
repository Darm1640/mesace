# -- coding: utf-8 --
{
    'name' : "Cancelar movimeintos de inventario LOTES",
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
        "stock",
        "account",
        "stock_account",
        "stock",
        "as_bo_account_stock",
        "dev_picking_cancel",
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