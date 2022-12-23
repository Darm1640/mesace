# -*- coding: utf-8 -*-
{
    'name': 'AhoraSoft Notificaciones Whatsapp Email',
    'version': '0.0.2',
    'category': 'account',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'account',
        "mail",
        'sale_management',
        'as_spectrocom_sales',
        'as_whatsapp_gateway',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/as_inherit_mail_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}