# -*- coding: utf-8 -*-

{
    "name" : "Automatic Import Lot/Serial Number with Purchase Process",
    "author": "Edge Technologies",
    "version" : "14.0.1.0",
    "live_test_url":'https://youtu.be/7h0rT_RIVWk',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Automatic Import Lot Number from purchase Automatic Import serial Number from purchase auto serial number import auto lot number import from purchase lot number import on receipt lot number import on picking serial number import on picking auto lot import',
    "description": """ Automatic Import Lot/Serial Number with Purchase Process.

     """,
    "license" : "OPL-1",
    'depends' : ['purchase','stock','purchase_stock'],
    'data': [
            'security/ir.model.access.csv',
            'views/purchase_res_config.xml',
            'wizard/purchase_automatic_lot_number.xml',
            'views/purchase_order_lot.xml'],
    "auto_install": False,
    "installable": True,
    "price": 28,
    "currency": 'EUR',
    "category" : "Warehouse",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
