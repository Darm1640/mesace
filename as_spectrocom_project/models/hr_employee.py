# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, _
class HrExpense(models.Model):
    _inherit = "hr.employee"

    as_vehiculo = fields.Many2one('fleet.vehicle', string="Vehiculo")
    as_numero_licencia = fields.Char(string='Nº Licencia')
    as_categoria = fields.Char(string='Categoria')
    as_vencimiento = fields.Date(string='Venc. L.C.', readonly=False)
    as_vencimiento_md = fields.Date(string='Venc. MD.', readonly=False)
    as_codigo_empleado = fields.Char(string='Codigo empleado')

    @api.onchange('as_vehiculo')
    def onchange_data(self):
        aux = 0