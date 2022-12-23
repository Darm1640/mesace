# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsSurveyRange(models.Model):
    """Modelo para guardar rango de modelos de campos para ser seleccionadfos en las encuentas"""
    _name = "as.survey.range"
    _descripcion = "Modelo para guardar rango de modelos de campos para ser seleccionadfos en las encuentas"

    name = fields.Char(string="Titulo")
    as_factor = fields.Float(string="Factor")
    as_range_lines = fields.One2many('as.survey.range.line','as_suverange_id')

class AsSurveyRangeLine(models.Model):
    """Modelo para guardar rango de modelos de campos para ser seleccionadfos en las encuentas lineas"""
    _name = "as.survey.range.line"
    _descripcion = "Modelo para guardar rango de modelos de campos para ser seleccionadfos en las encuentas lineas"

    as_from = fields.Float(string="Desde")
    as_to = fields.Float(string="Hasta")
    as_value = fields.Float(string="Valor")
    as_suverange_id = fields.Many2one('as.survey.range', string='Rango')

