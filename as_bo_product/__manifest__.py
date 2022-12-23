# -*- coding: utf-8 -*-
{
    'name' : "Ahorasoft NUCLEO - Productos",
    'version': '1.0.9',
    'category': 'product',
    'author': 'AhoraSoft',
    'summary': 'Customized product Management for Chile',
    'website': 'http://www.ahorasoft.com',
    'depends' : ['base','product','account','contacts',],
    'data': [
        'security/ir.model.access.csv',
        'security/as_group_restricciones.xml',
        'views/as_product_template.xml',
        'views/as_sequence_product.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

