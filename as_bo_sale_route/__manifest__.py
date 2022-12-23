# -*- coding: utf-8 -*-
{
    'name': 'Rutas Customización en Ventas',
    'version': '1.3.3',
    'category': 'Stock',
    'author': 'Ahorasoft',
    'summary': 'Customized Warehouse Management for Bolivia',
    'website': 'http://www.ahorasoft.com',
    'depends': [
        'base',
        'base_setup',
        'stock',
        'sale',
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/as_cuadro_personal_retirado_pdf.xml',
        'views/as_cuadro_personal_retirado.xml',
        'wizard/as_resumen_ventas_gestion.xml',
        'wizard/as_cuadro_personal_retirado.xml',
        'wizard/as_cuadro_beneficios_sociales.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}