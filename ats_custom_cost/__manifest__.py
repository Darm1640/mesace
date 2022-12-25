# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ats_custom_costs',
    'version': '14.0.1',
    'images': ['static/description/icon.jpg'],
    'category': 'Sale',
    'description': """
Custom view cost and margin's products
========================================
    """,
    'author': 'ATSOLUTIONS S.A.S',
    'website': 'http://www.atsolutions.com.co',
    'license':'OPL-1',
    'depends': ['base', 'sale_management'],
    'data': [
        # Security
        'security/groups.xml',
        # Views
        'views/product_views.xml',
        #'views/sale_order_views.xml',
    ],
    'qweb': [],
    'application': False,
    'installable': True,
}
