# -*- coding: utf-8 -*-
{
    'name': "Website Ecommerce Order Customer Comment / Message",
    'version': '2.1.2',
    'category': 'Website/Website',
    'license': 'Other proprietary',
    'price': 19.0,
    'currency': 'EUR',
    'summary':  """Allow your customer to send message from website ecommerce shop.""",
    'description': """
Website Order Customer Comment
customer message
website order customer message
website ecommerce order message

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'http://probuseappdemo.com/probuse_apps/website_order_customer_comment/439',#'https://youtu.be/c6e7kiVL2Q8',
    'depends': [
        'sale_management',
        'website_sale',
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': False,
}
