# -*- coding: utf-8 -*-
##############################################################################
#
#    Harhu IT Solutions
#    Copyright (C) 2020-TODAY Harhu IT Solutions(<https://www.harhu.com>).
#    Author: Harhu IT Solutions(<https://www.harhu.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Hide prices for public users',
    'summary': 'Hide prices for all products from specific website for public user configurable',
    'version': '14.0.0.1.0',
    'category': 'website',
    'author': 'Harhu IT Solutions',
    'maintainer': 'Harhu IT Solutions',
    'contributors': ["Harhu IT Solutions"],
    'website': 'http://www.harhu.com',
    'live_test_url': 'https://www.harhu.com/contactus',
    'depends': ['website_sale', 'website_sale_wishlist', 'website_sale_comparison'],
    'data': [
        'views/asserts.xml',
        'views/website_view.xml',
        'views/website_template.xml',
    ],
    'price': 15.00,
    'currency': "USD",
    'license': 'LGPL-3',
    'images': ['static/description/poster_image.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
