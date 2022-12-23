# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import re
import xlrd
from xlrd import open_workbook
import base64
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
_logger = logging.getLogger(__name__)

class as_hr_employees(models.Model):
    _name="as.hr.employees"
    _description="empleados a seleccionar"

    as_generador_id = fields.Many2one('as.generate.bonus.discount', string='Procesamiento de Nomina')
    as_employee_ids = fields.One2many( 'as.hr.employees.line', 'as_generator_id',string='Empleados')
    reason_id = fields.Many2one(
        'as.bonus.reason', 
        string='Motivo de bonificación',required=True
    )
    as_selector = fields.Boolean(string='Seleccionar todo')

    @api.onchange('as_selector')
    def as_get_selector(self):
        for emp in self:
            for line in emp.as_employee_ids:
                line.as_action = emp.as_selector

    @api.model
    def default_get(self, fields):
        res = super(as_hr_employees, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        dictline = []
        dictlinestock = []
        stock = 1
        menor = 0.0
        value = 0.0
        if res_ids and res_ids[0]:
            so_line = res_ids[0]
            so_line_obj = self.env['as.generate.bonus.discount'].browse(so_line)
            employees = self.env['hr.employee'].search([])
            for emp in employees: 
                if emp.contract_id.as_wage_bisemanal > 0:       
                    vasl={
                        'as_employee_id': emp.id,
                    }
                    dictline.append([0, 0, vasl])

                res.update({
                    'as_employee_ids':dictline,
                })
            return res
 

    def as_get_cargar_empleados(self):
        self.ensure_one()
        cont = len(self.as_generador_id.as_summary_ids)
        cont+=1
        for employee in self.as_employee_ids:
            if employee.as_action:
                vals = {
                    'as_employee_id': employee.as_employee_id.id,
                    'as_generator': self.as_generador_id.id,
                    'reason_id': self.reason_id.id,
                    'as_bonus_amount': 1,
                    'as_modalidad': 'auto',
                    'as_cantidad': self.as_generador_id.as_cantidad,
                    'as_date_start': self.as_generador_id.as_date_start,
                    'as_sequencia': cont
                }
                if employee.as_employee_id.contract_id.as_wage_bisemanal > 0:
                    vals['as_bonus_amount'] = employee.as_employee_id.contract_id.as_wage_bisemanal
                    vals['as_modalidad'] = 'auto'
                bonus_line = self.env['as.bonus.discount.line'].sudo().create(vals)
                bonus_line.as_get_date_end()
                cont+=1


      

class as_hr_employees_line(models.Model):
    _name="as.hr.employees.line"
    _description="empleados a seleccionar"

    as_employee_id = fields.Many2one('hr.employee', string='Empleado')
    as_action = fields.Boolean(string='Seleccionar')
    as_generator_id = fields.Many2one('as.hr.employees', string='padre')