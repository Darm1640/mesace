# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from datetime import date
import xlrd
import base64
import datetime
import math
import re

TYPE_INCREASE = [('ipc', 'IPC'), ('fixed', 'Fixed'), ('minimum_wage', 'Minimum Wage'), ('manual', 'Manual')]
TYPE_SALARY = [('sueldo_basico', 'SUELDO BÁ?SICO'),
               ('salario_integral', 'SALARIO INTEGRAL'),
               ('apoyo_sostenimiento', 'APOYO SOSTENIMIENTO')]


class HrSalaryIncrease(models.Model):
    _name = 'hr.salary.increase'
    _description = 'Salary increase for ipc and percentage'

    name = fields.Char()
    state = fields.Selection(selection=[('draft', 'Draft'), ('done', 'Done')],
                             default='draft')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    tipo_de_salario_contrato = fields.Selection([
        ('SUELDO BÁSICO', 'SUELDO BÁSICO'),
        ('SALARIO INTEGRAL', 'SALARIO INTEGRAL'),
        ('APOYO SOSTENIMIENTO', 'APOYO SOSTENIMIENTO')],
        tracking=True)

    type_increase = fields.Selection(selection=TYPE_INCREASE, string='Selection')
    increase_lines_ids = fields.One2many('hr.salary.increase.lines', 'salary_increase_id')
    date = fields.Date('Executed Date')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')
    min_amount = fields.Float('Min Amount')
    max_amount = fields.Float('Max Amount')

    charge_employee_xlsx = fields.Boolean('Charge Employee Xlsx')
    file = fields.Binary('File')
    type_aprentice_sena = fields.Selection([
        ('lective', 'Lective Stage'),
        ('productive', 'Productive Stage')])

    def load_data(self):
        for rec in self:
            if rec.file:
                workbook = xlrd.open_workbook(
                    file_contents=base64.decodestring(
                        rec.file))
                row_list = []
                last_sheet = workbook.sheet_by_index(-1)
                for row in range(1, last_sheet.nrows):
                    row_list.append(last_sheet.row_values(row))
                for line_list in row_list:
                    rec_data = {
                        'salary_increase_id': rec.id,
                        'employee_id': None,
                        'contract_id': None,
                        'current_wage': 0,
                        'new_wage': float(line_list[1]) if rec.type_increase == 'manual' else 0,
                    }
                    if line_list[0]:
                        employee = self.env['hr.employee'].search([('identification_id', '=', int(line_list[0]))])
                        if employee:
                            contract = self.env['hr.contract'].search(
                                [('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)
                            if contract:
                                rec_data.update({
                                    'contract_id': contract.id,
                                    'current_wage': contract.wage,
                                })
                            rec_data.update({'employee_id': employee.id})

                    if rec_data:
                        rec_data.update({'salary_increase_id': rec.id})
                        self.env['hr.salary.increase.lines'].create(rec_data)

            else:
                raise exceptions.UserError(_('No file uploaded yet '))

    def charge_employee(self):
        today = date.today()
        config = self.env['hr.payroll.config'].search(
            [('start_date', '<=', today), ('end_date', '>=', today), ('state', '=', 'done'),
             ('company_id', '=', self.company_id.id)])

        if not config:
            config = self.env['hr.payroll.config'].search(
                [('start_date', '<=', today), ('end_date', '>=', today), ('state', '=', 'done')])

        if not config:
            raise exceptions.ValidationError(_('No configuration for this year'))

        contracts = []
        contracts_integral = []

        if self.type_increase == 'ipc':

            ipc_rate = self.env['hr.payroll.config.lines'].search(
                [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'IPC')])

            if not ipc_rate:
                raise exceptions.ValidationError(_('No ipc configuration for this year'))

            contracts = self.env['hr.contract'].search(
                [('wage', '>=', self.min_amount), ('tipo_de_salario_contrato', '=', self.tipo_de_salario_contrato),
                 ('wage', '<=', self.max_amount), ('active', '=', True),
                 ('state', '=', 'open')])

        if self.type_increase == 'fixed':
            contracts = self.env['hr.contract'].search(
                [('wage', '>=', self.min_amount), ('tipo_de_salario_contrato', '=', self.tipo_de_salario_contrato),
                 ('wage', '<=', self.max_amount), ('active', '=', True),
                 ('state', '=', 'open')])

        if self.type_increase == 'minimum_wage':
            min_wage = self.env['hr.payroll.config.lines'].search(
                [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Minimo')])

            integral_salary = self.env['hr.payroll.config.lines'].search(
                [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Integral')])

            if not integral_salary:
                raise exceptions.ValidationError(_('No integral salary configuration for this year'))

            contracts = self.env['hr.contract'].search(
                [('wage', '<', min_wage.value), ('tipo_de_salario_contrato', '=', self.tipo_de_salario_contrato),
                 ('active', '=', True),
                 ('state', '=', 'open')])

            contracts_integral = self.env['hr.contract'].search(
                [('tipo_de_salario_contrato', '=', 'salario_integral'), ('wage', '<', integral_salary.value),
                 ('active', '=', True), ('state', '=', 'open')])

        if contracts or contracts_integral:
            self.increase_lines_ids.unlink()
            if contracts and self.tipo_de_salario_contrato == 'apoyo_sostenimiento' and self.type_aprentice_sena:
                contracts = contracts.filtered(lambda j: j.type_apprentice_sena == self.type_aprentice_sena)
            if contracts_integral and self.tipo_de_salario_contrato == 'apoyo_sostenimiento' and self.type_aprentice_sena:
                contracts_integral = contracts_integral.filtered(
                    lambda j: j.type_apprentice_sena == self.type_aprentice_sena)
            for contract in contracts:
                vals = {
                    'employee_id': contract.employee_id.id,
                    'salary_increase_id': self.id,
                    'contract_id': contract.id,
                    'current_wage': contract.wage,
                }
                self.env['hr.salary.increase.lines'].create(vals)

            for contract in contracts_integral:
                vals = {
                    'employee_id': contract.employee_id.id,
                    'salary_increase_id': self.id,
                    'contract_id': contract.id,
                    'current_wage': contract.wage,
                }
                self.env['hr.salary.increase.lines'].create(vals)

        if not self.increase_lines_ids:
            raise exceptions.ValidationError(_('No employees available to increase'))

    def increase_salary(self):
        if self.increase_lines_ids:
            today = fields.Date.today()
            config = self.env['hr.payroll.config'].search(
                [('start_date', '<=', today), ('end_date', '>=', today), ('state', '=', 'done')])

            percentage = 0

            if self.type_increase == 'ipc':
                ipc_rate = self.env['hr.payroll.config.lines'].search(
                    [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'IPC')])

                percentage = ipc_rate.value
                if percentage <= 0:
                    raise exceptions.ValidationError(_('The percentage must be greater than 0'))

                for line in self.increase_lines_ids:
                    wage = line.contract_id.wage
                    increase = (wage * percentage / 100)
                    wage = increase + wage
                    line.write({
                        'new_wage': wage
                    })

            if self.type_increase == 'fixed':
                percentage = self.percentage

                if percentage <= 0:
                    wage = self.amount
                    for line in self.increase_lines_ids:
                        line.write({
                            'new_wage': wage
                        })
                else:
                    for line in self.increase_lines_ids:
                        wage = line.contract_id.wage
                        increase = (wage * percentage / 100)
                        wage = increase + wage
                        line.write({
                            'new_wage': wage
                        })

            if self.type_increase == 'minimum_wage':
                min_wage = self.env['hr.payroll.config.lines'].search(
                    [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Minimo')])

                integral_salary = self.env['hr.payroll.config.lines'].search(
                    [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Integral')])

                for line in self.increase_lines_ids:
                    increase = 0
                    if line.contract_id.tipo_de_salario_contrato == 'salario_integral':
                        increase = integral_salary.value
                    else:
                        increase = min_wage.value
                    wage = increase
                    line.write({
                        'new_wage': wage
                    })

            self.date = date.today()
            self.state = 'done'

        else:
            raise exceptions.ValidationError(_('No employees available to increase'))

    @api.model
    def create(self, vals):
        vals['name'] = _('Salary Increase - ') + str(date.today())
        return super(HrSalaryIncrease, self).create(vals)


class HrSalaryIncreaseLines(models.Model):
    _name = 'hr.salary.increase.lines'

    salary_increase_id = fields.Many2one('hr.salary.increase')

    employee_id = fields.Many2one('hr.employee', 'Employee')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    tipo_de_salario_contrato = fields.Selection(selection=TYPE_SALARY,
                                                tracking=True,
                                                related='contract_id.tipo_de_salario_contrato')
    current_wage = fields.Float()
    new_wage = fields.Float()

    @api.onchange('employee_id')
    def _charge_fields(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)

            if contract:
                self.contract_id = contract.id
                self.current_wage = contract.wage
