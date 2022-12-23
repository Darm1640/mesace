# -*- coding: utf-8 -*-
{
    'name': 'AhoraSoft Facturacion Boliviana RND 101800000026',
    'version': '1.2.8',
    'category': 'Invoicing',
    'author': 'Ahorasoft',
    'summary': 'Customized Invoicing for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'account',
        'uom',
        
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/as_report_format.xml',
        'views/report/as_report_invoice_new.xml',
        'views/report/as_report_invoice_preliminar.xml',
        'views/as_account_invoice.xml',
    ],
    "external_dependencies": {
        "python": ['xmltodict'], 
        "bin": []},
    'installable': True,
    'application': True,
    'auto_install': False,

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
}