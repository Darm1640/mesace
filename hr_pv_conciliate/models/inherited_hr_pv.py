# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pytz
import datetime
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import float_compare
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError, ValidationError, Warning
from ip2geotools.databases.noncommercial import DbIpCity
from odoo.http import request
import math


class HrpvEvent(models.Model):
    _inherit = 'hr.pv.event'

    is_leave_calculate = fields.Boolean('Leave Calculate', tracking=True)
    spending = fields.Boolean('Spending', tracking=True)
    exploitation = fields.Boolean('Exploitation', tracking=True)
    employee_balance = fields.Boolean('Employee Balance', tracking=True)
    range_id = fields.Many2one('hr.event.range', tracking=True)
    event_conciliate_id = fields.Many2one(
        'hr.pv.event', 'Event Conciliate', tracking=True)

    @api.onchange('is_leave_calculate')
    def onchange_is_leave_calculate(self):
        """If not leave calculate then no range."""
        if not self.is_leave_calculate:
            self.range_id = ''


class Hrpv(models.Model):
    _inherit = 'hr.pv'

    is_leave_calculate = fields.Boolean(
        related='event_id.is_leave_calculate', store=True)
    value_leave = fields.Float(
        compute='_compute_value_leave', digits=(16, 2), store=True,
        tracking=True)
    conciliate_id = fields.Many2one('hr.pv.conciliation', tracking=True, copy=False)
    partner_con_id = fields.Many2one('res.partner', tracking=True)
    summatory_amount = fields.Float(related="conciliate_id.summatory_amount")
    different_amount = fields.Float(related="conciliate_id.different_amount")
    balance_to_conciliate = fields.Float(related="conciliate_id.balance_to_conciliate")
    state_conciliate = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('conciliate', 'Conciliate'),
        ('reject', 'Reject'),
        ('tramited', 'Tramited')], string='Status', copy=False,
        related="conciliate_id.state", store=True)
    conciliate_pv_id = fields.Many2one('hr.pv.conciliation')

    @api.depends('event_id', 'event_id.range_id.line_ids', 'fix_wage_amount', 'start_date', 'end_date')
    def _compute_value_leave(self):
        for rec in self:
            rec.value_leave = 0.0
            value = 0.0
            if rec.event_id and rec.event_id.is_leave_calculate and rec.event_id.range_id:
                if rec.contract_id.check_integral_salary:
                    day_salary = (rec.fix_wage_amount * 0.7) / 30
                else:
                    day_salary = rec.fix_wage_amount / 30
                for line in rec.event_id.range_id.line_ids:
                    if rec.total_days_calendar >= line.max_days:
                        value += (line.max_days - line.min_days + 1) * day_salary * line.percentage / 100
                    elif rec.total_days_calendar < line.max_days and rec.total_days_calendar >= line.min_days:
                        value += (rec.total_days_calendar - line.min_days + 1) * day_salary * line.percentage / 100
                rec.value_leave = math.ceil(value)

    @api.onchange('is_arl')
    def clear_fields_arl(self):
        if self.is_arl == True:
            self.is_eps = False
            self.partner_con_id = self.employee_id.arl_id

    @api.onchange('is_eps')
    def clear_fields_eps(self):
        res = {}
        if self.is_eps == True:
            self.is_arl = False
            self.partner_con_id = self.employee_id.eps_id
            if self.employee_id and self.employee_id.eps_id and self.employee_id.eps_id.required_physical_evidence:
                res = {
                    'warning': {
                        'title': _('Warning!'),
                        'message': _("You have to delivery leave phisical evidence")}
                }
        return res

    def action_conciliate(self):
        for rec in self:
            if rec.conciliate_id:
                raise ValidationError(_("Conciliate Repeated."))
            hr_pv_conciliation_rec = self.env['hr.pv.conciliation'].create({
                'employee_id': rec.employee_id.id,
                'pv_id': rec.id,
            })
            rec.conciliate_id = hr_pv_conciliation_rec.id
        return {
            "name": "Hr Pv Conciliate",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "hr.pv.conciliation",
            "type": "ir.actions.act_window",
            "res_id": hr_pv_conciliation_rec.id,
        }

    def see_conciliate(self):
        for rec in self:
            if rec.conciliate_id:
                return {
                    "name": "Hr Pv Conciliate",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_model": "hr.pv.conciliation",
                    "type": "ir.actions.act_window",
                    "res_id": rec.conciliate_id.id,
                }

    # @api.constrains('conciliate_id')
    # def _check_conciliate_id(self):
    #    for rec in self:
    #        if rec.conciliate_id and self.search_count([
    #                ('conciliate_id', '=', rec.conciliate_id.id)]) > 1:
    #            raise ValidationError(_(
    #                "Conciliate Repeated."))
