# -- coding: utf-8 --
{
    'name' : "Ahorasoft SPECTROCOM Reparaciones",
    'version' : "1.5.4",
    'author'  : "Ahorasoft",
    'description': """
Webservice dummy SPECTROCOM
===========================

Custom module for Latproject
    """,
    'category' : "Uncategorized",
    'depends' : [
        "base",
        "repair",
        "as_spectrocom_sales",
        "sale"
        ],
    'website': 'http://www.ahorasoft.com',
    'data' : [
            'security/ir.model.access.csv',
            'wizard/as_repair_historial.xml',
            'views/as_repair_order.xml',
            'views/as_repair_order_modificar.xml',
            'views/as_repair_historial.xml',
            'report/as_repair_historial.xml',
            'views/as_repair_recepcion_equipos.xml',
            'views/as_repair_orden_trabajo.xml',
            'views/report/as_repair_recepcion_equipos.xml',
            'views/report/as_repair_orden_trabajo.xml',
            'views/as_repair_sheet.xml',
            'views/as_repair_order_informe_reparaciones.xml',
            'views/report/as_repair_order_informe_reparaciones.xml',
            'views/as_repair_order_sheet_informe_reparaciones.xml',
            'views/report/as_repair_order_sheet_informe_reparaciones.xml',
            'views/as_proposal_conditions.xml',
            'views/as_sequence.xml',
            'views/as_stock_move.xml',
            'views/as_res_company.xml',
             ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}