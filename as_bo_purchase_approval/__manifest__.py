# -*- coding: utf-8 -*-
{
    'name': 'Aprobación de Compras',
    'version': '1.0.4',
    'category': 'purchase',
    'author': 'Ahorasoft',
    'summary': 'Niveles de aprobación para compras',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'purchase',
        'base_user_role',
        'project',
    ],
    'data': [
        # 'security/as_group_view.xml',
        'security/ir.model.access.csv',
        'views/as_level_approval.xml',
        'views/as_purchase_order.xml',
        'data/as_template_email.xml',
       
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}