# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _name= 'as.hr.worked.days'

    name = fields.Char('Nombre')
    code = fields.Char('Codigo')

