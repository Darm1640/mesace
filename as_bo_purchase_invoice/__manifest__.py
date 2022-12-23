# -*- coding: utf-8 -*-
{
    'name': 'AhoraSoft Factura de Compra',
    'version': '1.3.7',
    'category': 'Stock',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'stock',
        'sale',
        'product',
        "purchase_stock",
        'sale_management',
        'report_xlsx',
        'purchase',
        'as_bo_configuration',
        'hr_expense',
        "hr",
    ],
    'data': [
        'security/as_group_view.xml',
        'security/ir.model.access.csv',
        'data/as_tipo_factura_proveedor.xml',
        'views/as_tipo_factura_view.xml',
        'views/as_invoice_supplier.xml',
        'views/as_res_config_setting.xml',
        'views/as_purchase.xml',
        'views/as_format_report.xml',
        'wizard/as_purchase_libro_compras.xml',
        'report/as_libro_compras_pdf.xml',
        'views/report/as_purchase_order_custom.xml',
        'views/as_hr_employee.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}