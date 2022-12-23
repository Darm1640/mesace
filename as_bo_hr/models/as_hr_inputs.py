# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _name= 'as.hr.inputs'

    name = fields.Char('Nombre')
    code = fields.Char('Codigo')

class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'
    _description = 'Payslip Input Type'

    as_recargo = fields.Char('Repocisión')