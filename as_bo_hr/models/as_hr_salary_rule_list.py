# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo import api, fields, models, _

class HrEmployeeRule(models.Model):
    _inherit = 'hr.salary.rule'

    as_account_debit_cost = fields.Many2one('account.account', string='Cuenta debito Costo')
    as_account_credit_cost = fields.Many2one('account.account', string='Cuenta credito Costo')