# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PayrollReport(models.Model):
    _name = 'hr.payroll.report'
    _order = 'code, id'
    _description = 'payroll  report'
    name = fields.Char(string='Name', required=True, help="Name")
    level = fields.Integer(string='level', help="Level", default=10)
    parent_id = fields.Many2one('hr.payroll.report',string='Padre', help='Level',)
    rule_ids = fields.Many2many('hr.salary.rule',string='Reglas', help='Level',)



