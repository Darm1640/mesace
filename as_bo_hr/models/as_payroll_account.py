# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=False, required=False,
        company_dependent=True,
        default=lambda self: self.env['account.journal'].search([
            ('type', '=', 'general'), ('company_id', '=', self.env.company.id)], limit=1))
