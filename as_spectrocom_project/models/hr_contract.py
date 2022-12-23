# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _


class HrExpense(models.Model):
    _inherit = "hr.contract"

    as_tipo_presupuesto = fields.Selection(selection=[('Fijo','Fijo'),('Frecuencia','Frecuencia')],default='Fijo', string="Tipo presupuesto")
    as_frecuencia = fields.Selection(selection=[('Mensual','Mensual'),('Trimestral','Trimestral'),('Anual','Anual')],default='Mensual', string="Frecuencia")
    as_monto = fields.Float(string='Monto')
    as_presupuesto_id = fields.One2many('as.presupuesto', 'as_contract_id', string="Presupuesto")

    def button_presupuesto(self):
        presupuesto = self.env['as.presupuesto']
        if not self.as_presupuesto_id:
            vals = {
                    'as_fecha_inicio':self.date_start,
                    'as_planificado':self.as_monto,
                    'as_ejecutado':0,
                    'as_diferencia':self.as_monto,
                }
            # for x in range(1):
            presupuesto.create(vals)
        else:
            presupuesto_modificado = presupuesto.sudo().search([('id', '=', self.as_presupuesto_id.id)])
            vals = {
                    'as_fecha_inicio':self.date_start,
                    'as_planificado':self.as_monto,
                    'as_ejecutado':0,
                    'as_diferencia':self.as_monto,
                }
            presupuesto_modificado.write(vals)
