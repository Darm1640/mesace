# -*- coding: utf-8 -*-
{
    'name': "lavish_account",

    'summary': """
        Módulo para personalización de la contabilidad Colombiana. """,

    'description': """
        Módulo para personalización de la contabilidad Colombiana. 
    """,

    'author': "lavish S.A.S",

    'category': 'account',
    'version': '0.1',

    'depends': ['base','account','account_reports','l10n_co_reports'],

    'data': [
        'security/ir.model.access.csv',
        'views/actions_payment_file.xml',
        'views/actions_account_account.xml',
        'views/actions_account_move.xml',
        'views/actions_exogenous_information.xml',
        'views/actions_res_partner_fe.xml',
        'views/menus.xml',
    ],
}
