# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsEmployee(models.Model):
    _inherit = "survey.survey"

    as_porcentaje = fields.Float(string="Porcentaje %")
    as_sequence = fields.Integer(string="Secuencia")
    as_parent_id = fields.Many2one('survey.survey', string='Padre')
    as_range_age_id = fields.Many2one('as.survey.range', string='Rango para Edad')
    as_range_old_id = fields.Many2one('as.survey.range', string='Rango para Antiguedad')