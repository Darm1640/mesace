# -*- coding: utf-8 -*-
{
    'name': "Tesoreria Localización Boliviana",
    'summary': """
        Modulo de Tesoreria Odoo14 enterprice
        """,
    'description': """
       Modulo de Tesoreria Odoo14 enterprice
    """,
    'author': 'Contabilidad Fiscal Facturas',
    'Maintainer':"Catherina Gomez",
    'website': 'http://www.ahorasoft.com/',
    'category': 'account',
    'version': '1.7.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'fleet',
        'sale',
        'report_xlsx',
        'as_bo_purchase_invoice',
        'as_bo_accounting',
        'as_bo_configuration',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/as_sales_config_setting.xml',
        'wizard/as_reason_checks.xml',
        'views/as_treasury.xml',
        'views/as_payment_multi.xml',
        'data/as_sequence.xml',
        'views/as_partner.xml',
        'wizard/as_ajustar_saldo.xml',
        'views/as_account_invoice.xml',
        'views/as_payment_acquirer.xml',
        'views/as_account_journal.xml',
        'views/as_check_control.xml',
        'views/as_deposit_digest.xml',
        'wizard/as_liquidation_tbank.xml',
        'wizard/as_report_checks.xml',
        'views/as_sale_view.xml',
        'views/as_caja_chica.xml',
        'views/as_product_name.xml',
        'views/as_res_config_settings.xml',
        'views/as_report_format.xml',
        'views/as_tipo_retencion.xml',
        'views/report/as_report_caja_chica_pdf.xml',
        'views/report/as_report_caja_chica_previa.xml',
        'views/report/as_report_caja_chica.xml',
    ],
    'qweb': [
        # 'static/src/xml/mobile_widget.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}
