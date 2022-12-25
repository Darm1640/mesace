# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Recruitment Reasons todoo',
    'version': '14.0.1.0',
    'author': 'Todoo SAS',
    'summary': 'Recruitment Reasons Customization for todoo',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'maintainer': 'todoo',
    'company': 'Todoo SAS',
    'website': 'TL soluciones',
    'depends': [
               'hr_recruitment',
    ],
    'data': [
        'views/recruitment_reason_view.xml',
        'views/inherited_recruitment_reason_view.xml',
        #'views/job_position_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
