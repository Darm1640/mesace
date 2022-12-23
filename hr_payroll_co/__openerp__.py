##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Opensystem Colombia (<http://opensystem.co>).
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
    'name': 'Nómina Colombiana',
    'version': '1.0',
    'author': 'Innovatecsa SAS e Interconsulting S.A',
    'category': 'Generic Modules/Human Resources',
    'depends': ['hr_payroll'],
    'demo': [],
    'description': """
Módulo de nómina para la localización colombiana
    """,
    'data': [
       'hr_payroll_co_view.xml', 
    ],
    'auto_install': False,
    'installable': True,
    'images': [],

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
