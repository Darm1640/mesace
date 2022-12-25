# -*- coding: utf-8 -*-
{
    'name': "Website Default Country",

    'summary': """
        Select the default country for an eCommerce Website""",

    'description': """
        Website Module to allow you to set the default country for a sale on the website.

        V1.1 - Added fix to allow module to work on single website applications
    """,

    'author': "Lily White Web",
    'website': "http://www.lilywhiteweb.com",
    'images':['static/description/default_country_screenshot.png'],
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
