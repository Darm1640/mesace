
from odoo import models, fields, api, _
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import calendar

class HreEmployee(models.Model):
    _inherit = 'hr.contract'

    as_wage_bisemanal = fields.Float(string="Quincena")