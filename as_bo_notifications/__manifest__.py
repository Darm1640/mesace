# -*- coding: utf-8 -*-
{
    'name': 'AhoraSoft Notificaciones Whatsapp',
    'version': '1.1.1',
    'category': 'account',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'account',
        'as_whatsapp_gateway',
        'base_user_role',
        "mail",
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/as_envio_notifications.xml',
        'data/as_ir_cron.xml',
        'data/as_template_email.xml',
        'views/as_res_configurations.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}