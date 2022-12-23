
from odoo import models, fields, api, _
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import calendar

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    as_bonus_discount_id = fields.Many2one('as.employee.bonus', string='Bono o descuento')


