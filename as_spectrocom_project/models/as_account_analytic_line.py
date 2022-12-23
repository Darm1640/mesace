# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _


class HrExpense(models.Model):
    _inherit = "account.analytic.line"

    as_tipo_contrato = fields.Char(string='Tipo contrato')
    as_duracion = fields.Integer(string='Duración')

    @api.onchange('as_tipo_contrato','employee_id')
    def onchange_contrato(self):
        self.as_tipo_contrato = self.employee_id.contract_id.structure_type_id.name

    @api.onchange('as_duracion')
    def onchange_tipo_contrato(self):
        if self.task_id.planned_hours:
            unidad_horas = self.env['uom.uom'].search([('name','=','Horas')])
            convertido = self.task_id.as_medida_tiempo._compute_quantity(self.as_duracion,unidad_horas,round=False)
            self.unit_amount = self.task_id.as_medida_tiempo._compute_quantity(self.as_duracion,unidad_horas,round=False)