# -- coding: utf-8 --
{
    'name' : "Ahorasoft SPECTROCOM correlacional",
    'version' : "1.1.3",
    'author'  : "Ahorasoft",
    'description': """
Webservice dummy SPECTROCOM
===========================

Custom module for Latproject
    """,
    'category' : "Uncategorized",
    'depends' : [
        "base",
        "sale",
        "stock",
        "crm",
        "mail",
        # "as_whatsapp_gateway",
        ],
    'website': 'http://www.ahorasoft.com',
    'data' : [
            # 'security/ir.model.access.csv',
            'views/as_crm.xml',
            'views/as_report_format.xml',
            'views/as_sequence.xml',
            'views/report/as_report_crm_lead.xml',
            'data/as_template_email.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}