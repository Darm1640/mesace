# -- coding: utf-8 --
{
    'name' : "Customizaciones en Contabilidad",
    'version' : "1.0.1",
    'author'  : "Ahorasoft",
    'description': """
Cutomizaciones para reparaciones y asientos contables de reparaciones
===========================

Custom module for MOTOPRO
    """,
    'category' : "account",
    'depends' : [
        "base",
        "account",
        ],
    'website': 'http://www.ahorasoft.com',
    'data' : [
            'security/ir.model.access.csv',
            'views/as_account_structure.xml',
            # 'views/as_account_move.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}