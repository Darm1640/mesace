# -*- coding: utf-8 -*-
{
    'name' : "Assets Management",
    'version' : "1.1.9",
    'description': """
Assets Module
===========================

Custom module for Assets register and management
    """,
    'category' : "Account",
    'depends' : [
                'base',
                 'product',
                 'sale',
                 'purchase',
                 'as_bo_configuration',
                 'om_account_asset','product',
                 'report_xlsx',
                 'account_accountant',
                 'as_bo_account_automatic',
                 'as_bo_accounting',
                 "product_brand",
        'sale_management',],
    'website': 'http://www.ahorasoft.com',
    'author' : "Ahorasoft",
    'data' : [
            # 'security/group_view.xml',
            'security/ir.model.access.csv',
            'wizard/as_account_move_lista_activos_fijos.xml',
            'wizard/as_ajustar_af_wiz.xml',
            'views/as_assets_custodies.xml',
            'views/as_assets_views.xml',
            #'data/res_currency.xml',
            'views/account_asset_category.xml',
            'report/as_assets_report_pdf.xml',
            'report/as_report_lista_activos_fijos_pdf.xml',
            'views/as_assets_format.xml',
            'wizard/as_cuadro_depreciacion_excel.xml',
            'wizard/as_generator_assets.xml',
            'views/as_asset_gestion.xml',
            'views/product_template.xml',
            'views/as_report_format.xml',
            'views/as_sale_order.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}