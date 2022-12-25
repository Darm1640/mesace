# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import calendar
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz
from odoo.exceptions import UserError, ValidationError, Warning

from odoo import models, api, fields, _
import math


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    total_remaining_approve_pv = fields.Integer(
        'Total Remaining Approve pv',
        compute='_compute_total_remaining_approve_pv')

    employee_bonus_ids = fields.One2many('hr.employee.bonus', 'employee_id', string='Employee Bonus')
    work_email = fields.Char(string='Work Email', tracking=True)
    copy_identification_id = fields.Binary(string="Copy Card Identification")
    file_name_copy_identification_id = fields.Char(tracking=True)
    date_childbirth = fields.Date(string="Date childbirth",
                                  tracking=True)

    def _compute_total_remaining_approve_pv(self):
        pv_obj = self.env['hr.pv']
        for record in self:
            record.total_remaining_approve_pv = pv_obj.search_count([
                ('employee_id.parent_id', '=', record.id),
                ('state', 'in', ['wait_comments', 'wait'])])

    def view_pv_records(self):
        pv_ids = self.env['hr.pv'].search([
            ('employee_id.parent_id', '=', self.id),
            ('state', 'in', ['wait', 'wait_comments'])])
        return {
            'name': _('pv'),
            'view_mode': 'tree,form',
            'res_model': 'hr.pv',
            'domain': [('id', '=', pv_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def round1(self, amount):
        return round(amount)

    def round100(self, amount):
        result = int(math.ceil(amount / 100.0)) * 100
        return result

    def round1000(self, amount):
        return round(amount, -3)

    def round2d(self, amount):
        return round(amount, 2)

    def get_pvs(self, date_to_payroll, event, def_amount='amount', def_return=True):
        """Get pv of current month and previous month approved."""
        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        if len(event_id) > 1:
            event_id = event_id.filtered(lambda x: x.company_id == self.env.company
                                                   or x.company_id == False)
            if len(event_id) > 1:
                raise ValidationError(
                    _('The name is in two events you must only one event with this name.'))
        if not event_id:
            event_id = self.env['hr.pv.event'].search([('code', '=', event)])
            if len(event_id) > 1:
                raise ValidationError(
                    _('The code is in two events you must only one event with this code.'))
        amount = 0

        if event_id:
            pv_ids = self.env['hr.pv'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])

            pv_used_ids = []

            date_from_payroll = datetime.date(date_to_payroll.year, date_to_payroll.month, 1)
            for pv in pv_ids:

                if def_amount == 'capital':
                    amount_pv = pv.capital_amount
                elif def_amount == 'interes':
                    amount_pv = pv.interest_amount
                elif pv.amount == 0:
                    amount_pv = pv.percentage
                else:
                    amount_pv = pv.amount

                if event_id.subtype_id.name == 'Ocasional':
                    if date_to_payroll and pv.start_date:
                        date_payroll = fields.Datetime.from_string(date_to_payroll)
                        date_payroll = date_payroll.replace(hour=11, minute=59)
                        start_date = fields.Datetime.from_string(pv.start_date)
                        date_from_payroll = fields.Datetime.from_string(date_from_payroll)
                        if start_date <= date_payroll and \
                                start_date >= date_from_payroll:  # and\
                            # not pv.after_close:

                            pv_used_ids.append(pv.id)
                            if event_id.affectation == 'deduction':
                                if pv.payment_type == 'both':
                                    amount += (amount_pv * -1) / 2
                                elif pv.payment_type == 'first' and date_to_payroll.day < 16:
                                    amount += (amount_pv * -1)
                                elif pv.payment_type == 'second' and date_to_payroll.day > 16:
                                    amount += (amount_pv * -1)
                                elif not pv.payment_type:
                                    amount += (amount_pv * -1)
                            else:
                                if pv.payment_type == 'both':
                                    amount += (amount_pv) / 2
                                elif pv.payment_type == 'first' and date_to_payroll.day < 16:
                                    amount += amount_pv
                                elif pv.payment_type == 'second' and date_to_payroll.day > 16:
                                    amount += amount_pv
                                elif not pv.payment_type:
                                    amount += amount_pv

                elif event_id.subtype_id.name == 'Fija':
                    if date_to_payroll and pv.start_date and pv.end_date:  # and\
                        # not pv.after_close:
                        date_payroll = fields.Datetime.from_string(date_to_payroll)
                        date_payroll_start = fields.Datetime.from_string(date_to_payroll.replace(day=1))
                        date_payroll_start = date_payroll_start.replace(hour=6)
                        start_date = fields.Datetime.from_string(pv.start_date)
                        end_date = fields.Datetime.from_string(pv.end_date)

                        if (start_date <= date_payroll and end_date >= date_payroll) or \
                            (start_date <= date_payroll and end_date >= date_payroll_start and \
                             end_date >= date_payroll):

                            pv_used_ids.append(pv.id)

                            if event_id.affectation == 'deduction':
                                if pv.payment_type == 'both':
                                    amount += (amount_pv * -1) / 2
                                elif pv.payment_type == 'first' and date_to_payroll.day < 16:
                                    amount += (amount_pv * -1)
                                elif pv.payment_type == 'second' and date_to_payroll.day > 16:
                                    amount += (amount_pv * -1)
                                elif not pv.payment_type:
                                    amount += (amount_pv * -1)
                            else:
                                if pv.payment_type == 'both':
                                    amount += (amount_pv) / 2
                                elif pv.payment_type == 'first' and date_to_payroll.day < 16:
                                    amount += amount_pv
                                elif pv.payment_type == 'second' and date_to_payroll.day > 16:
                                    amount += amount_pv
                                elif not pv.payment_type:
                                    amount += amount_pv

                    elif date_to_payroll and pv.start_date and not pv.end_date:  # and\
                        #  not pv.after_close:
                        date_payroll = fields.Datetime.from_string(date_to_payroll)
                        start_date = fields.Datetime.from_string(pv.start_date)

                        pv_used_ids.append(pv.id)

                        if event_id.affectation == 'deduction':
                            if pv.payment_type == 'both':
                                amount += (amount_pv * -1) / 2
                            elif pv.payment_type == 'first' and date_to_payroll.day < 16:
                                amount += (amount_pv * -1)
                            elif pv.payment_type == 'second' and date_to_payroll.day > 16:
                                amount += (amount_pv * -1)
                            elif not pv.payment_type:
                                amount += (amount_pv * -1)
                        else:
                            if pv.payment_type == 'both':
                                amount += (amount_pv) / 2
                            elif pv.payment_type == 'first' and date_to_payroll.day < 16:
                                amount += amount_pv
                            elif pv.payment_type == 'second' and date_to_payroll.day > 16:
                                amount += amount_pv
                            elif not pv.payment_type:
                                amount += amount_pv

                if event_id.distribution_by_days:
                    start_date = fields.Datetime.from_string(pv.start_date)
                    end_date = fields.Datetime.from_string(pv.end_date) if pv.end_date else False

                    amount = self.calculate_distribution_by_day(date_from_pv=start_date, date_to_pv=end_date,
                                                                date_to_payroll=date_to_payroll,
                                                                amount=pv.amount)

            if def_return:
                return amount
            else:
                pv_ids_used = self.env['hr.pv'].search([('id', 'in', pv_used_ids)])
                return pv_ids_used

        else:
            if def_return:
                return 0.0
            else:
                return False

    def calculate_distribution_by_day(self, date_from_pv, date_to_pv, date_to_payroll, amount):
        if date_from_pv and date_to_pv:
            date_parcial = date_to_pv - date_from_pv
            amount_parcial = (amount / int((date_parcial.days + 1)))
        if date_from_pv and not date_to_pv:
            days = 30
            amount_parcial = amount / days

        days_payroll = date_to_payroll - (date_from_pv.date())
        amount = amount_parcial * days_payroll.days

        return amount

    def get_pvs_before(self, date_to_payroll, event):
        """Get pv of current month and previous month approved."""
        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        amount = 0
        if event_id:
            pv_ids = self.env['hr.pv'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])
            date_from_payroll = datetime.date(date_to_payroll.year, date_to_payroll.month, 1)
            for pv in pv_ids:
                if event_id.subtype_id.name == 'Ocasional':
                    if date_to_payroll and pv.start_date:
                        date_payroll = fields.Datetime.from_string(date_to_payroll)
                        date_payroll = date_payroll.replace(hour=11, minute=59)
                        start_date = fields.Datetime.from_string(pv.start_date)
                        date_from_payroll = fields.Datetime.from_string(date_from_payroll)
                        if start_date <= date_payroll:  # and not pv.after_close:
                            if event_id.affectation == 'deduction':
                                amount += (pv.amount * -1)
                            else:
                                amount += pv.amount
            return amount
        else:
            return 0.0

    def get_days_pvs(self, date_from_payroll, date_to_payroll, event):
        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        if not event_id:
            event_id = self.env['hr.pv.event'].search([('code', '=', event)])
        days = 0
        if event_id:
            pv_ids = self.env['hr.pv'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])
            for pv in pv_ids:
                if date_to_payroll and date_from_payroll and pv.start_date and pv.end_date:
                    date_from_pay = fields.Datetime.from_string(date_from_payroll)
                    date_from_pay = date_from_pay.replace(hour=00, minute=00)
                    date_to_pay = fields.Datetime.from_string(date_to_payroll)
                    date_to_pay = date_to_pay.replace(hour=11, minute=59)
                    start_date = fields.Datetime.from_string(pv.start_date)
                    end_date = fields.Datetime.from_string(pv.end_date)
                    if start_date <= date_from_pay and end_date <= date_to_pay:
                        diff = relativedelta(end_date, date_from_pay)
                    elif start_date <= date_from_pay and end_date > date_to_pay:
                        diff = relativedelta(date_to_pay, date_from_pay)
                    elif start_date > date_from_pay and end_date <= date_to_pay:
                        diff = relativedelta(end_date, start_date)
                    elif start_date > date_from_pay and end_date > date_to_pay:
                        diff = relativedelta(date_to_pay, start_date)
                if diff.months:
                    days = diff.months * 30
                if diff.days:
                    days = diff.days + days
        return days

    def get_days_pvs_enc(self, date_from_payroll, date_to_payroll, event):
        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        if not event_id:
            event_id = self.env['hr.pv.event'].search([('code', '=', event)])
        days = 0
        days_acu = 0
        if event_id:
            pv_ids = self.env['hr.pv'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])
            for pv in pv_ids:
                if date_to_payroll and date_from_payroll and pv.start_date and pv.end_date:
                    date_from_pay = fields.Datetime.from_string(date_from_payroll)
                    date_from_pay = date_from_pay.replace(hour=00, minute=00)
                    date_to_pay = fields.Datetime.from_string(date_to_payroll)
                    date_to_pay = date_to_pay.replace(hour=11, minute=59)
                    start_date = fields.Datetime.from_string(pv.start_date)
                    end_date = fields.Datetime.from_string(pv.end_date)
                    if start_date <= date_from_pay and end_date <= date_to_pay:
                        diff = relativedelta(end_date, date_from_pay)
                        diffacu = relativedelta(end_date, start_date)
                    elif start_date <= date_from_pay and end_date > date_to_pay:
                        diff = relativedelta(date_to_pay, date_from_pay)
                        diffacu = relativedelta(date_to_pay, start_date)
                    elif start_date > date_from_pay and end_date <= date_to_pay:
                        diff = relativedelta(end_date, start_date)
                        diffacu = relativedelta(end_date, start_date)
                    elif start_date > date_from_pay and end_date > date_to_pay:
                        diff = relativedelta(date_to_pay, start_date)
                        diffacu = relativedelta(date_to_pay, start_date)
                if diff.months:
                    days = diff.months * 30
                if diff.days:
                    days = diff.days + days
                if diffacu.months:
                    days_acu = diffacu.months * 30
                if diffacu.days:
                    days_acu = diffacu.days + days_acu
        return (days, days_acu)

    def get_acumulate_month_before(self, date, configuration):
        """Function to fetch previous month acumulate."""
        conf_id = self.env['hr.conf.acumulated'].search(
            [('name', '=', configuration)])
        result = 0
        date1 = fields.Date.from_string(date)
        if date.month != 1 and conf_id:
            if conf_id:
                last_day_of_prev_month = date1.replace(day=1) - timedelta(days=1)
                start_day_of_prev_month = date1.replace(day=1) - timedelta(days=last_day_of_prev_month.day)
                payslips = self.env['hr.payslip'].search(
                    [('date_from', '>=', start_day_of_prev_month),
                     ('date_to', '<=', last_day_of_prev_month),
                     ('employee_id', '=', self.id)])
                acumulate_employee_ids = self.env['hr.employee.acumulate'].search(
                    [('employee_id', '=', self.id),
                     ('hr_rules_acumulate_id', '=', conf_id.id),
                     ('pay_slip_id', 'in', payslips.ids)
                     ])
                if acumulate_employee_ids:
                    for acumulate in acumulate_employee_ids:
                        result += acumulate.total_acumulate
        elif date.month == 1 and self.previous_regimen and conf_id:
            if conf_id:
                last_day_of_prev_month = date1.replace(day=1) - timedelta(days=1)
                start_day_of_prev_month = date1.replace(day=1) - timedelta(days=last_day_of_prev_month.day)
                payslips = self.env['hr.payslip'].search(
                    [('date_from', '>=', start_day_of_prev_month),
                     ('date_to', '<=', last_day_of_prev_month),
                     ('employee_id', '=', self.id)])
                acumulate_employee_ids = self.env['hr.employee.acumulate'].search(
                    [('employee_id', '=', self.id),
                     ('hr_rules_acumulate_id', '=', conf_id.id),
                     ('pay_slip_id', 'in', payslips.ids)
                     ])
                if acumulate_employee_ids:
                    for acumulate in acumulate_employee_ids:
                        result += acumulate.total_acumulate
        return result

    def get_acumulate_month_actual(self, date, configuration):
        """Function to fetch previous month acumulate."""
        conf_id = self.env['hr.conf.acumulated'].search(
            [('name', '=', configuration)])
        result = 0
        if date.month and conf_id:
            date1 = fields.Date.from_string(date)
            if conf_id:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(day=1)
                payslips = self.env['hr.payslip'].search(
                    [('date_from', '>=', start_day_of_prev_month),
                     ('date_to', '<=', last_day_of_prev_month),
                     ('employee_id', '=', self.id)])
                acumulate_employee_ids = self.env['hr.employee.acumulate'].search(
                    [('employee_id', '=', self.id),
                     ('hr_rules_acumulate_id', '=', conf_id.id),
                     ('pay_slip_id', 'in', payslips.ids)
                     ])
                if acumulate_employee_ids:
                    for acumulate in acumulate_employee_ids:
                        result += acumulate.total_acumulate
        return result

    def get_year_accumulate(self, configuration):
        """Function to fetch year accumulate."""
        conf_id = self.env['hr.conf.acumulated'].search(
            [('name', '=', configuration)])
        result = 0
        if conf_id:
            payslips = self.env['hr.payslip'].search(
                [('employee_id', '=', self.id)])
            accumulate_employee_ids = self.env['hr.employee.acumulate'].search(
                [('employee_id', '=', self.id),
                 ('hr_rules_acumulate_id', '=', conf_id.id),
                 ('pay_slip_id', 'in', payslips.ids)
                 ])
            for accumulate in accumulate_employee_ids:
                result += accumulate.total_acumulate
        return result

    def get_value_line_payslip_before(self, payslip, rules, month=12, year=0):
        """Function to fetch year accumulate month before."""
        result = 0
        if payslip.date_from.month == 1:
            year = payslip.date_from.year - 1
            month = 12
        elif payslip.date_from.month == 7:
            year = payslip.date_from.year
            month = 6
        else:
            year = payslip.date_from.year
            month = payslip.date_from.month - 1
        date = payslip.date_from.replace(day=15, month=month, year=year)
        payslip = self.env['hr.payslip'].search([
            ('employee_id', '=', self.id),
            ('date_from', '<=', date),
            ('date_to', '>=', date)
        ])
        if payslip.line_ids:
            for line in payslip.line_ids:
                if line.salary_rule_id.name in (rules):
                    result += line.total
        return result

    def get_value_line_payslip_year_before(self, payslip, rules, month=12, year=0):
        """Function to fetch year accumulate month before."""
        result = 0
        if payslip.date_from.month == 2:
            year = payslip.date_from.year - 1
            month = 12
        date = payslip.date_from.replace(day=25, month=month, year=year)
        payslip = self.env['hr.payslip'].search([
            ('employee_id', '=', self.id),
            ('date_from', '<=', date),
            ('date_to', '>=', date)
        ])
        if payslip.line_ids:
            for line in payslip.line_ids:
                if line.salary_rule_id.name in (rules):
                    result += line.total
        return result

    def get_value_total_payslip_month_actual(self, payslip, rules):
        """Function to fetch year accumulate month before."""
        result = 0
        date = payslip.date_from.replace(day=1)
        payslips = self.env['hr.payslip'].search([
            ('employee_id', '=', self.id),
            ('date_from', '>=', date),
            ('date_to', '<=', payslip.date_to),
            ('state', 'in', ('done', 'paid'))
        ])
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.salary_rule_id.name in (rules):
                    result += line.total
        return result

    def get_average_paid_annual_or_wage(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.id == 0:
            return 0
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ) \
                            and not line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env['hr.payslip.worked_days'].search([
                    ('payslip_id', '=', payslip.id),
                    ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        # Calculate before three months is the same salary Basic
        last_day_of_prev_month = date1.replace(day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        for p_id in payslips:
            acc_salary = 0
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ) \
                        and not line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += line.total
            if valmonthbefore == round(accum_month) and acc_salary == valmonthbefore:
                acc_salary = (acc_salary / 30) * self.get_days_annual(payslip.date_to)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    def get_average_paid_annual_less_pay31(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.id == 0:
            return 0
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ) \
                            and not line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary - p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                          p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env['hr.payslip.worked_days'].search([
                    ('payslip_id', '=', payslip.id),
                    ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            # if days_exclude != 0 or result_days < 30 and result_days > 0:
            #    if result_days > 30:
            #        result_days = 30
            #    accum_month = (accum_month/30)*result_days
            # if result_days < 0 and accum_month > 0:
            #    accum_month = (accum_month/30)*result_days
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        last_day_of_prev_month = date1.replace(day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        if self.entry_date.year == payslip.date_to.year and \
                self.entry_date.month > auxmonthbegin:
            return result
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    accum_month = round(accum_month - \
                                        p_id.contract_id.fix_wage_amount / 30)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        auxmonth = 0
        for p_id in payslips:
            acc_salary = 0
            days_month = 1
            days_month_entry = 1
            if p_id.date_to.year == self.entry_date.year and \
                    p_id.date_to.month == self.entry_date.month:
                days_month_entry = sum([work_days.number_of_days for work_days
                                        in p_id.worked_days_line_ids])
                days_month = 30
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ) \
                        and not line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += round((line.total / days_month_entry) * (days_month))
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    acc_salary = round(acc_salary - \
                                       p_id.contract_id.fix_wage_amount / 30)
            if acc_salary == valmonthbefore:
                auxmonth += 1
            if valmonthbefore == round(accum_month) and \
                    acc_salary == valmonthbefore and auxmonth == 2:
                acc_salary = (acc_salary / 30) * self.get_days_annual(payslip.date_to)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    def get_average_paid_annual(self, date, payslip):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.id == 0:
            return 0
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in ('BASIC', 'AUS', 'AUSINC', 'AUXTRANS') \
                            and not line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in ('BASIC', 'AUS', 'AUSINC', 'AUXTRANS'):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env['hr.payslip.worked_days'].search([
                    ('payslip_id', '=', payslip.id),
                    ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    def get_average_paid_annual_termination(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.id == 0:
            return 0
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        if date:
            raise ValidationError(
                _("Teh process don't have date in function get_average_paid_annual_termination."))

        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(month=12, day=31)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ) \
                            and not line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary - p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                          p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env['hr.payslip.worked_days'].search([
                    ('payslip_id', '=', payslip.id),
                    ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if days_exclude != 0 or result_days < 30 and result_days > 0:
                if result_days > 30:
                    result_days = 30
                accum_month = (accum_month / 30) * result_days
            if result_days < 0 and accum_month > 0:
                accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        last_day_of_prev_month = date1.replace(day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        if self.entry_date.year == payslip.date_to.year and \
                self.entry_date.month > auxmonthbegin:
            return result
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    accum_month = round(accum_month - \
                                        p_id.contract_id.fix_wage_amount / 30)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        auxmonth = 0
        for p_id in payslips:
            acc_salary = 0
            days_month = 1
            days_month_entry = 1
            if p_id.date_to.year == self.entry_date.year and \
                    p_id.date_to.month == self.entry_date.month:
                days_month_entry = sum([work_days.number_of_days for work_days
                                        in p_id.worked_days_line_ids])
                days_month = 30
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ) \
                        and not line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += round((line.total / days_month_entry) * (days_month))
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and \
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    acc_salary = round(acc_salary - \
                                       p_id.contract_id.fix_wage_amount / 30)
            if acc_salary == valmonthbefore:
                auxmonth += 1
            if valmonthbefore == round(accum_month) and \
                    acc_salary == valmonthbefore and auxmonth == 2:
                acc_salary = (acc_salary / 30) * self.get_days_annual(payslip.contract_id.date_end)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    def get_average_paid_biannual_termination(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.id == 0:
            return 0
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        if date.month == 12 and payslip.date_from.month == 1:
            date1 = fields.Date.from_string(payslip.date_from)
        else:
            date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 6:
                last_day_of_prev_month = date1.replace(month=6, day=30)
                start_day_of_prev_month = date1.replace(month=1, day=1)
            else:
                last_day_of_prev_month = date1.replace(month=12, day=31)
                start_day_of_prev_month = date1.replace(month=7, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ) \
                            and not line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env['hr.payslip.worked_days'].search([
                    ('payslip_id', '=', payslip.id),
                    ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if days_exclude != 0 or result_days < 30 and result_days > 0:
                if result_days > 30:
                    result_days = 30
                accum_month = (accum_month / 30) * result_days
            if result_days < 0 and accum_month > 0:
                accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        # Calculate before three months is the same salary Basic
        last_day_of_prev_month = date1.replace(day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        for p_id in payslips:
            acc_salary = 0
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ) \
                        and not line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += line.total
            if valmonthbefore == round(accum_month) and acc_salary == valmonthbefore and \
                    result_days == 30:
                acc_salary = (acc_salary / 30) * self.get_days_annual(payslip.contract_id.date_end)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    def get_average_paid_biannual(self, date, payslip, list_categ=(
            'BASIC', 'AUS', 'AUSINC', 'AUXTRANS', 'AJUSSAL', 'AUSAJUS')):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.id == 0:
            return 0
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        date1 = fields.Date.from_string(date)
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 6:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=1, day=1)
            else:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=7, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ) \
                            and not \
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                    ('payslip_id', '=', payslip.id),
                    ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    def get_average_paid_quarterly(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        if payslip.id == 0:
            return 0
        date1 = fields.Date.from_string(date)
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 3:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=1, day=1)
            else:
                last_day_of_prev_month = date1.replace(day=calendar.monthrange(date1.year, date1.month)[1])
                start_day_of_prev_month = date1.replace(month=date1.month - 2, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ):
                        accum_salary += line.total
            for p_id in payslip_now:
                for line in p_id.ps_input_rf_ids:
                    if line.rule_id.category_id.code in (list_categ):
                        accum_month += line.value_final
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    def get_average_paid_quarterly_biannual(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        date1 = fields.Date.from_string(date)
        if payslip.id == 0:
            return 0
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 3:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=1, day=1)
            elif date1.month in (7, 8):
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=7, day=1)
            else:
                last_day_of_prev_month = date1.replace(day=calendar.monthrange(date1.year, date1.month)[1])
                start_day_of_prev_month = date1.replace(month=date1.month - 2, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ):
                        accum_salary += line.total
            for p_id in payslip_now:
                for line in p_id.ps_input_rf_ids:
                    if line.rule_id.category_id.code in (list_categ):
                        accum_month += line.value_final
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    def day_week_friday(self, date):
        if date and date.strftime("%w") == '5':
            return True
        return False

    def create_wizard(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Create PV'),
                'res_model': 'hr.create.pv.wizard',
                'target': 'new',
                'view_id': self.env.ref('hr_payroll_variations.create_pv_wizard_view_form').id,
                'view_mode': 'form',
                'context': {'default_employee_id': self.id}
                }


class HrEmployeeBonusType(models.Model):
    _name = "hr.employee.bonus.type"
    _description = "Model for storing type bonus cards"

    name = fields.Char(string='Name', required=True)


class HrEmployeeBonus(models.Model):
    _name = "hr.employee.bonus"
    _description = "Model for storing bonus cards"
    _rec_name = "bonus_type"

    name = fields.Char(string='Name')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)
    bank_id = fields.Many2one(comodel_name='res.bank', string='Bank')
    bonus_type = fields.Many2one(comodel_name='hr.employee.bonus.type', string='Bonus Type')
    card = fields.Char(string='Target product')
    number = fields.Char(string='Visa code')
    tn = fields.Char('T.N')

    @api.model
    def create(self, vals):
        vals['name'] = self.employee_id.name + self.card
        return super(HrEmployeeBonus, self).create(vals)


class HrEmployeeSena(models.Model):
    _name = "hr.employee.sena"
    _description = "Model for storing monetization code sena"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code', required=True)
    name_occupation = fields.Char(string='Name Occupation', required=True)

    @api.model
    def create(self, vals):
        vals['name'] = vals.get('code') + "/" + vals.get('name_occupation')
        return super(HrEmployeeSena, self).create(vals)
