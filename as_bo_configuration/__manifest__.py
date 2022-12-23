# -*- coding: utf-8 -*-
{
    'name' : "Ahorasoft General Configurations",
    'version' : "14.0.5",
    'author' : "Ahorasoft",
    'description': """
General Configurations Module
===========================

Custom module with general configurations for other Ahorasoft Modules
    """,
    'category' : "Administration",
    'depends' : ['base','account','product','stock','sale'],
    'website': 'http://www.ahorasoft.com',
    'author' : "Ahorasoft",
    'data' : [
        'security/group_view.xml',
        'security/ir.model.access.csv',
        'views/as_account_move.xml',
        'views/as_excel_txt.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}