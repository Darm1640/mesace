# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _name= 'as.hr.employee.afp'
    _description = "Modelo para almacenar información de las AFPs" 

    name = fields.Char('Nombre')