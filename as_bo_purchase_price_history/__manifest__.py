# -*- coding: utf-8 -*-
{
    'name': 'Historial de precios de compra',
    
    'author' : 'Ahorasoft',
    
    'website': 'https://www.softhealer.com',
    
    "support": "support@softhealer.com",
        
    'version': '1.0.0',
    
    'category': 'Purchases',

    'summary': """
show product cost history app, product purchase record module, product cost price history, show product past record odoo
""",

    'description': """This module useful to show the history of the cost price for the product, you can also track the history of the cost price of the product for different suppliers. Easy to find rates given to you by the supplier in the past for that product.
show product cost history app, product purchase record module, product cost price history, show product past record odoo
""",
    
    'depends': ['purchase'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/purchase_price_history.xml',
    ],
    'images': ['static/description/background.png', ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
    "price": 15,
    "currency": "EUR"        
}
