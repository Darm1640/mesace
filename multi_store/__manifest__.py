##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Multi Stores Management',
    'version': "15.0.1.0.0",
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/multi_store_security.xml',
        'views/res_store_view.xml',
        'views/res_users_view.xml',
        'views/stock_picking_type_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_warehouse_view.xml',
        'views/account_journal_views.xml',
        'views/account_move_line_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/res_store_views.xml',
    ],
    'demo': [
        'demo/res_store_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
