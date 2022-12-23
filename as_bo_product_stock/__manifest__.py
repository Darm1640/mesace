# -*- coding: utf-8 -*-
{
    "name": "Stocks and Cost by Locations",
    "version": "1.0.7",
    "category": "Warehouse",
    "author": "Ahorasoft",
    "website": "http://www.ahorasoft.com",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "sale_stock",
        "purchase_stock",
        "as_bo_purchase_import",
    ],
    "data": [
        "views/views.xml",
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
        "views/sale_order.xml",
        "views/res_users_view.xml",
        "views/stock_picking.xml",
        "views/as_product_template.xml",
        "wizard/as_actualizador_stock.xml",
    ],
    "qweb": [
        "static/src/xml/locations_hierarchy.xml"
    ],
    "js": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make inventory data essential and comfortable for elaboration",
    "description": """
    Salespersons and warehouse managers mostly work with a single location. Staff from Madrid would hardly make quotations for clients from Berlin. That is why aggregated Odoo stocks levels are awkward to use. Surely, you might push a few buttons, apply groupings and filters to retrieve required product information. However, is it comfortable? Hardly. Moreover, it is confusing since sudden misunderstanding leads to inexecutable promises. So, you need a tool to provide essential inventory data <strong>at a glance</strong>, but to keep details by locations <strong>easy-reach</strong> and <strong>clear</strong>. Here it comes! 

    User default warehouse
    Expandable locations' hierarchy
    Inventory for product variants, templates, and sale lines
    Excel table inventories by locations
    Inventory levels on product variant form (minimized view)
    Inventory levels on product variant form (fully expanded view)
    Salespersons and warehouse managers default warehouse (preferences)
    Sales order warehouse is applied based on salesperson warehouse
    Stocks by locations from sales orders and quotations (opened)
    Stocks by locations from sales orders and quotations (to open)
    Inventories by locations on product template form 
    Standard inventory figures are calculated for default warehouse only (kanban view)
    Standard inventory figures are calculated for default warehouse only (tree view)
    Users settings to apply default warehouse
    The xlsx table of inventory levels
    I faced the error: QWeb2: Template 'X' not found
  
""",
    "images": [
        "static/description/main.png"
    ],
    "currency": "BOB",
}