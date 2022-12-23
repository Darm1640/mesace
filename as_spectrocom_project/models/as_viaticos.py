# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AsRquestMaterials(models.Model):
    """Modulo para viaticos"""
    _name = "as.viaticos"
    _description = 'Modulo para almacenar viaticos'
    _rec_name = "as_name"

    name = fields.Char(string="Titulo")
    as_empleado = fields.Many2one('hr.employee', 'Empleado', required=True)
    as_name = fields.Many2one('product.product', 'Descripcion')
    as_cant_dias = fields.Integer('Cantidad de dias')
    as_precio_unitario = fields.Float('Precio unitario')
    as_presupuestado = fields.Float('Total presupuestado')
    as_ejecutado = fields.Float('Total ejecutado')
    as_diferencia = fields.Float('Diferencia')
    as_project_id = fields.Many2one('project.task', string="Proyecto")
    as_estado = fields.Selection([
        ('draft', 'Borrador'),
        ('to_approval', 'Para Aprobar'),
        ('approval', 'Aprobado')
    ], string='Estado Viatico', default='draft')


    @api.onchange('as_cant_dias','as_precio_unitario')
    def onchange_presupuestado(self):
        self.as_presupuestado = self.as_cant_dias * self.as_precio_unitario
    
    @api.onchange('as_presupuestado','as_ejecutado')
    def onchange_diferencia(self):
        self.as_diferencia = self.as_presupuestado - self.as_ejecutado

    @api.onchange('as_name')
    def onchange_descripcion(self):
        hr_expense = self.env['hr.expense']
        if self.as_name:
            producto = self.as_name
            project_task = self.as_project_id
            as_empleado = self.as_empleado
            hr_expense_modificado = hr_expense.sudo().search([('employee_id', '=', as_empleado.id),('product_id', '=', producto.id),('project_id', '=', project_task.id.origin)])
            hr_expense_modificado.as_presupuesto_line = self.id.origin
            if hr_expense_modificado.state == 'approved':
                self.as_ejecutado = hr_expense_modificado.total_amount
                self.onchange_diferencia()
                
    @api.onchange('as_empleado')
    def activar_lineas_viaticos(self):
        vali=0
        if self.as_empleado:
            valuee=''
        else:
            if self.as_project_id.user_id.id:
                valores=''
            else:
                empleado_linea_poner = self.env['hr.employee'].sudo().search([('user_id', '=', self.as_project_id.user_id.id)])
                if len(empleado_linea_poner) > 1:
                    self.as_empleado = ''
                else:
                    self.as_empleado = empleado_linea_poner.id.name
            # else:
            #     raise UserError(_("verifique que sus empleados tengan asignado un Usuario"))