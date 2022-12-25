# -*- coding: utf-8 -*-

{
    'name': 'Customer Credit Limit',
    'category': 'Sales',
    'version': '13.0',
    'author': 'SprintERP',
    'website': 'http://www.sprinterp.com',
    'summary': 'This plugin use for check Customer Credit Limit and notify to sales manager.',
    'description':"""
        This plugin use for check Customer Credit Limit and notify to sales manager.
    """,
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'wizard/wizard_view.xml',
        'views/views.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'price':25,
    'currency':'EUR',
}