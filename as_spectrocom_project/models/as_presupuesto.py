# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _

class AsRquestMaterials(models.Model):
    """Modulo para presupuesto"""
    _name = "as.presupuesto"
    _description = 'Modulo para almacenar presupuesto'

    name = fields.Char(string="Titulo")
    as_fecha_inicio = fields.Date('Fecha inicio')
    as_fecha_fin = fields.Date('Fecha fin')
    as_planificado = fields.Float('Planificado')
    as_ejecutado = fields.Float('Ejecutado')
    as_diferencia = fields.Float('Diferencia')
    as_contract_id = fields.Many2one('hr.contract', string="Contrato")