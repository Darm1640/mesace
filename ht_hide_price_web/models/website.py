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

from odoo import models, fields


class Website(models.Model):

    _inherit = 'website'

    hide_price = fields.Boolean(string='Hide Price?')
    email = fields.Char(string='Mail To')
