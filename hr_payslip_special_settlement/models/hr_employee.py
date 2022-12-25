# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
import datetime
from odoo import models, api, fields, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_days_exclude_payslip(self, date):
        days_exclude = 0
        leaves_type_ids = self.env['hr.leave.type'].search([
            ('exclude_calculate_payslip', '=', True)])
        payslip_ids = self.env['hr.payslip'].search([
            ('employee_id', '=', self.id),
            ('date_from', '>=', date)]).ids
        for leave_type in leaves_type_ids:
            worked_days_line_ids = self.env['hr.payslip.worked_days'].search([
                ('employee_id', '=', self.id),
                ('code', '=', leave_type.name)])
            days_exclude += sum([work_days.number_of_days for work_days
                                 in worked_days_line_ids \
                                 if not work_days.contract_id.exclude_from_seniority])
        return days_exclude

    def get_days_biannual(self, date_to_payroll):
        month = date_to_payroll.month
        if month > 6:
            type_id = self.env['type.settlement'].search(
                [('pay_type', '=', 'biannual'),
                 ('end_month', '=', '12')])
        else:
            type_id = self.env['type.settlement'].search(
                [('pay_type', '=', 'biannual'),
                 ('end_month', '=', '6')])
        contract = self.env['hr.contract']
        contract_id = contract.search([
            ('employee_id', '=', self.id),
            ('exclude_from_seniority', '=', False)],
            order='date_start asc', limit=1)
        if contract_id.date_start.year < date_to_payroll.year:
            contract_date_simulate = datetime.date(date_to_payroll.year, 1, 1)
        else:
            contract_date_simulate = contract_id.date_start
        total_days = 0
        if date_to_payroll and type_id:
            assign_month_ids = \
                type_id.assign_month_ids.filtered(
                    lambda t:
                    month >= int(t.start_month) >= contract_date_simulate.month)
            for assign_id in assign_month_ids:
                if contract_date_simulate.month == assign_id.start_month:
                    if contract_date_simulate.day == 1:
                        total_days += assign_id.days_assign
                    else:
                        if assign_id.end_day > 30:
                            assign_id.end_day = 30
                        total_days = \
                            assign_id.end_day - contract_date_simulate.day + 1
                elif date_to_payroll.month == assign_id.end_month:
                    if date_to_payroll.day == assign_id.end_day:
                        total_days += assign_id.days_assign
                    else:
                        total_days += date_to_payroll.day
                else:
                    total_days += assign_id.days_assign
        date_payslip = datetime.date(date_to_payroll.year, \
                                     int(type_id.start_month), type_id.start_day)
        total_days = total_days - self.get_days_exclude_payslip(date_payslip)
        return total_days

    def get_days_annual(self, date_to_payroll):
        month = date_to_payroll.month
        type_id = self.env['type.settlement'].search(
            [('pay_type', '=', 'annual')])
        contract = self.env['hr.contract']
        contract_id = contract.search([
            ('employee_id', '=', self.id),
            ('exclude_from_seniority', '=', False)],
            order='date_start asc', limit=1)
        if contract_id.date_start.year < date_to_payroll.year:
            contract_date_simulate = datetime.date(date_to_payroll.year, 1, 1)
        else:
            contract_date_simulate = contract_id.date_start
        total_days = 0
        if date_to_payroll and type_id:
            assign_month_ids = \
                type_id.assign_month_ids.filtered(
                    lambda t:
                    month >= int(t.start_month) >= contract_date_simulate.month)
            for assign_id in assign_month_ids:
                if contract_date_simulate.month == assign_id.start_month and \
                        date_to_payroll.month != assign_id.end_month:
                    if contract_date_simulate.day == 1:
                        total_days += assign_id.days_assign
                    else:
                        if assign_id.end_day > 30 or assign_id.end_month == 2:
                            assign_id.end_day = 30
                        total_days = \
                            assign_id.end_day - contract_date_simulate.day + 1
                elif date_to_payroll.month == assign_id.end_month:
                    if date_to_payroll.day == assign_id.end_day:
                        total_days += assign_id.days_assign
                    else:
                        if date_to_payroll.day >= 30:
                            total_days += 30
                        else:
                            total_days += date_to_payroll.day
                else:
                    total_days += assign_id.days_assign
        date_payslip = datetime.date(date_to_payroll.year, \
                                     int(type_id.start_month), type_id.start_day)
        total_days = total_days - self.get_days_exclude_payslip(date_payslip)
        return total_days

    def calculate_year_input(self, payslip):
        restriction = 0
        entry_date = str(self.entry_date) + ' ' + '00:00:00'
        start = datetime.datetime.strptime(entry_date, '%Y-%m-%d %H:%M:%S')
        if start.year < 1991:
            restriction = 1
        return restriction

    def calculate_days_compensation(self, payslip):
        days_result = 0
        if payslip:
            employee = self
            if employee.entry_date:
                if payslip.contract_completion_id:
                    today = str(payslip.contract_completion_id.date) + ' ' + '00:00:00'
                else:
                    today = str(payslip.date_to) + ' ' + '00:00:00'
                entry_date = str(employee.entry_date) + ' ' + '00:00:00'
                start = datetime.datetime.strptime(entry_date, '%Y-%m-%d %H:%M:%S')
                ends = datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(ends, start)
                if ends.day > start.day:
                    diff.days += 1
                if diff.days == 31:
                    diff.days = 30
                if ends.month == 2:
                    if ends.year % 4 == 0:
                        if ends.day == 29:
                            diff.days += 1
                    else:
                        if ends.day == 28:
                            diff.days += 2
                days_result = diff.days + diff.months * 30 + diff.years * 360
        return days_result

    def get_days_leave(self, leave, payslip):
        total = 0
        allocation_ids = self.env['hr.leave.allocation'].search(
            [('holiday_status_id', '=', leave),
             ('employee_id', '=', self.id),
             ('state', '=', 'validate')])
        total_allocation = sum([allocation.number_of_days_display for allocation
                                in allocation_ids])
        leave_ids = self.env['hr.leave'].search(
            [('holiday_status_id', '=', leave),
             ('employee_id', '=', self.id),
             ('state', '=', 'validate')])
        total_leaves = sum([leave.number_of_days_display for leave
                            in leave_ids])
        total = total_allocation - total_leaves
        start_date = str(payslip.date_from) + ' ' + '00:00:00'
        end_date = str(payslip.date_to) + ' ' + '00:00:00'
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        ends = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        diff = relativedelta(ends, start)
        days_month = int(diff.days) + 1
        if days_month > 30 or ends.day >= 28:
            days_month = 30
        if ends.month == 2:
            if ends.day >= 28:
                days_month = 30
        days_accu = (1.25 / 30) * days_month
        total = total + days_accu
        return total

    def imprimir_valores(self, value, name):
        print("MAPFFF11Value", value)
        print("MAPFFF11name", name)
        return True

    def holidays_month_actual(self, date, payslip):
        allocation_ids = self.env['hr.leave.allocation'].search([
            ('holiday_status_id.autocalculate_leave', '=', True),
            ('employee_id', '=', self.id),
            ('state', '=', 'validate')])
        total_allocation = sum([allocation.number_of_days_display for allocation in allocation_ids])
        leave_ids = self.env['hr.leave'].search([
            ('holiday_status_id.autocalculate_leave', '=', True),
            ('employee_id', '=', self.id),
            ('state', '=', 'validate'),
            ('request_date_to', '<=', date)])
        total_leaves = sum([leave.number_of_days_display for leave
                            in leave_ids])
        total = total_allocation - total_leaves
        start_date = str(payslip.date_from) + ' ' + '00:00:00'
        end_date = str(payslip.date_to) + ' ' + '23:59:59'
        days_month = 0
        if payslip.date_from != payslip.date_to:
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            ends = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            diff = relativedelta(ends, start)
            days_month = int(diff.days) + 1

            if days_month > 30 or ends.day >= 28:
                days_month = 30
            if ends.month == 2:
                if ends.day >= 28:
                    days_month = 30
        result_days = sum([work_days.number_of_days for work_days
                           in payslip.worked_days_line_ids])
        if result_days < 0:
            days_month += result_days - 1
        days_accu = round((1.25 / 30) * days_month, 2)
        total = total + days_accu
        return total

    def calculate_days_compensation_tf(self, payslip):
        days_result = 0
        if payslip:
            employee = self
            if payslip.contract_id.date_end:
                date_from = str(payslip.date_to) + ' ' + '00:00:00'
                date_to = str(payslip.contract_id.date_end) + ' ' + '00:00:00'
                start = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
                ends = datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(ends, start)
                diff.days
                if diff.days == 31:
                    diff.days = 30
                days_result = diff.days + diff.months * 30 + diff.years * 360
        return days_result

    def get_holidays_retroactive(self, date_payroll, event):
        """Get holidays between dates pv."""
        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        total_days = 0
        if event_id:
            pv_ids = self.env['hr.pv'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])
            for pv in pv_ids:
                leave_ids = self.env['hr.leave'].search([
                    ('holiday_status_id.autocalculate_leave', '=', True),
                    ('employee_id', '=', self.id),
                    ('state', '=', 'validate'),
                    ('request_date_to', '>=', pv.start_date),
                    ('request_date_from', '<=', date_payroll)])
                for leave in leave_ids:
                    l_start = str(leave.request_date_from) + ' ' + '00:00:00'
                    l_end = str(leave.request_date_to) + ' ' + '00:00:00'
                    l_start = datetime.datetime.strptime(l_start, '%Y-%m-%d %H:%M:%S')
                    l_end = datetime.datetime.strptime(l_end, '%Y-%m-%d %H:%M:%S')
                    if pv.start_date <= l_start:
                        start = l_start
                    else:
                        start = pv.start_date
                    if pv.end_date <= l_end:
                        ends = pv.end_date
                    else:
                        ends = l_end
                    diff = relativedelta(ends, start)
                    days = int(diff.days)
                    if ends.month == 2:
                        if ends.day >= 28:
                            days += 2
                    total_days = days
        return total_days

    def get_workdays_retroactive(self, date_payroll, event):
        """Get pv of current month and previous month approved."""
        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        total_days = 0
        if event_id:
            pv_ids = self.env['hr.pv'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])
            for pv in pv_ids:
                start = pv.start_date
                ends = pv.end_date
                diff = relativedelta(ends, start)
                days = int(diff.days) + int(diff.months) * 30
                if diff.days > 30:
                    days -= 1
                if ends.month == 2:
                    if ends.day >= 28:
                        days += 2
                total_days = days - self.get_holidays_retroactive(date_payroll, event)
        return total_days
