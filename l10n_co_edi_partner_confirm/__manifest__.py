# -*- coding: utf-8 -*-
{
    'name': 'Confirmacion de cliente FE',
    'summary': 'Confirmacion de cliente FE',
    'author': 'Gustavo H.',
    'version': '14.0.1.0',
    'depends': [
        'l10n_co_edi_jorels',
    ],
    'data': [
        'data/mail_template_data.xml',
        'views/account_move_view.xml',
        'data/dian_cron.xml',
    ],
    'installable': True,
    'post_init_hook': '_account_post_init',
}
