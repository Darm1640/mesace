# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz
from odoo.exceptions import ValidationError


class HrUVTValueRF(models.Model):
    _inherit = "hr.value.uvt.rf"

    deduction_employee_id = fields.Many2one(
        'hr.deductions.rf.employee', string="Deduction",
        tracking=True)

    r_ded_rent_exempt_value = fields.Float(
        string="Value exempt deductions recalc",
        tracking=True)
    r_ded_rent_exempt_percetage = fields.Float(
        string="Percetage exempt deductions recalc",
        tracking=True)
    r_rent_exempt_value = fields.Float(
        string="Value exempt deductions recalc",
        tracking=True)
    r_rent_exempt_percetage = fields.Float(
        string="Percetage exempt deductions recalc",
        tracking=True)
    r_total_ded_exempt_percetage = fields.Float(
        string="Total percentage ded and excemp rent",
        tracking=True)
    r_total_ded_exempt_value = fields.Float(
        string="Total value ded and excemp rent", tracking=True)
