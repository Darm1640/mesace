# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError, Warning


class Hrpv(models.Model):
    """Hr PV. Human Resources Payroll Variants"""
    _inherit = 'hr.pv'

    deduction_employee_id = fields.Many2one(
        'hr.deductions.rf.employee', string="Deduction",
        tracking=True)
    percentage = fields.Float(string='Percentage', readonly=True, tracking=True,
                              states={'draft': [('readonly', False)]})

    def create_withholding(self):
        if self.event_id.deduction_id:
            wi_id = self.env['hr.deductions.rf.employee'].create({
                'name': self.event_id.deduction_id.name,
                'hr_deduction_type_id': self.event_id.deduction_id.type_id.id,
                'hr_deduction_id': self.event_id.deduction_id.id,
                'value': self.amount,
                'percentage': self.percentage,
                'employee_id': self.employee_id.id,
                'active': True,
                'start_date': self.start_date,
                'end_date': self.end_date,
            })
            self.write({'deduction_employee_id': wi_id.id})
        else:
            raise ValidationError(_(
                'Please configure value in event for withholding income.'))
        return True

    def action_approve(self):
        res = super(Hrpv, self).action_approve()
        if self.event_id.income_withholding:
            self.create_withholding()
        return res

    def action_draft(self):
        if self.deduction_employee_id:
            raise ValidationError(_(
                'This process cannot be completed, '
                'because it has a deduction associated with it. '
                'You can be cancel this PV to inactive deduction.'))
        else:
            res = super(Hrpv, self).action_draft()
        return res

    @api.model
    def create(self, vals):
        res = super(Hrpv, self).create(vals)  # Save the form
        for item in res:
            if item.event_id.income_withholding:
                item_ids = self.search([
                    ('end_date', '>=', item.start_date),
                    ('employee_id', '=', item.employee_id.id),
                    ('event_id', '=', item.event_id.id),
                    ('id', '<>', res.id),
                    ('state', 'not in', ('rejected', 'cancel', 'processed'))])
                for item_id in item_ids:
                    item_id.write({'state': 'processed'})
                    if item_id.deduction_employee_id:
                        item_id.deduction_employee_id.write({'active': False})

                item_ids = self.search([
                    ('end_date', '=', False),
                    ('employee_id', '=', item.employee_id.id),
                    ('event_id', '=', item.event_id.id),
                    ('id', '<>', res.id),
                    ('state', 'not in', ('rejected', 'cancel', 'processed'))])
                for item_id in item_ids:
                    item_id.write({'state': 'processed'})
                    if item_id.deduction_employee_id:
                        item_id.deduction_employee_id.write({'active': False})
        return res


class HrpvEvent(models.Model):
    """HR PV Event"""
    _inherit = 'hr.pv.event'

    income_withholding = fields.Boolean(string='Income Withholding',
                                        tracking=True)
    deduction_id = fields.Many2one(
        'hr.deduction.rf', string="Deduction",
        tracking=True)
