# -*- coding: utf-8 -*-
{
    'name': 'Aprobación de Facturas de Proveedor',
    'version': '1.0.0',
    'category': 'account',
    'author': 'Ahorasoft',
    'summary': 'Niveles de aprobación para Facturas de Proveedor',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'account',
        'base_user_role',
        'project',
        'as_bo_purchase_approval',
    ],
    'data': [
        # 'security/as_group_view.xml',
        'security/ir.model.access.csv',
        'views/as_level_approval.xml',
        'views/as_account_move.xml',
        'data/as_template_email.xml',
       
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}