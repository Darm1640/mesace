# -*- coding: utf-8 -*-
{
    'name': "lavish_erp",

    'summary': """
        lavish ERP""",

    'description': """
        .lavish ERP.
    """,

    'author': "lavish S.A.S",
    #'website': "http://www.lavish.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'lavishERP',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','contacts',
        'account',
        'account_tax_python',
        'l10n_co',
        'base_address_city',
        "purchase",
        "sale"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/report_execute_query.xml',
        'views/res_country_state.xml',
        'views/res_country_view.xml',
        'views/product_category_view.xml',
        'views/account_move_view.xml',
        'views/general_actions.xml',
        #'views/res_partner.xml',
        'views/res_users.xml',
        'views/actions_alerts.xml',
        'views/lavish_confirm_wizard.xml',
        'views/general_menus.xml'       
    ]    
}
