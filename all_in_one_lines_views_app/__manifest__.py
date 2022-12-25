# -*- coding: utf-8 -*-
{
    'name': 'All in one Order Line Views',
    "author": "Edge Technologies",
    'version': '14.0.1.0',
    'live_test_url': "https://youtu.be/UyVuxNkfYjg",
    "images":['static/description/main_screenshot.png'],
    'summary': "All in one Lines Views order line views for all sale order line view purchase order line view invoice line view stock move view stock move line view line kanban view for all vendor bill line view PO line view SO line view sale line view purchase line view",
    'description': """ 
        All in one Lines Views for sale/quotation and Request/purchse order,  invoice/credit note and bill/refund, and picking operations.
    """,
    "license" : "OPL-1",
    'depends': ['sale_management','purchase','stock','account'],
    'data': [
        'security/all_in_security.xml',
        'views/all_in_one_sale.xml',
        'views/all_in_one_purchse.xml',
        'views/stock_operstion.xml',
        'views/account_invoice.xml',
        ],
    'installable': True,
    'auto_install': False,
    'price': 25,
    'currency': "EUR",
    'category': 'Sales',
}
