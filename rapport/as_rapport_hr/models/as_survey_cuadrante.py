# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsSurveyCuadrante(models.Model):
    _name = "as.survey.cuadrante"
    _description = "Cuadrante de talento"

    name = fields.Char(string="Nombre Talento", required=True)
    as_code = fields.Char(string="Código",required=True)
    as_range_start = fields.Float(string="Rango (inicio)",required=True)
    as_range_end = fields.Float(string="Rango (Fin)",required=True)
    as_features_ids = fields.Many2many('as.survey.features', string='Tag Características')
    as_color_id = fields.Many2one('as.survey.color', string='Color',required=True)

class AsCaracteristicas(models.Model):
    _name = "as.survey.features"
    _description = "Tag de Caracteristicas"

    name = fields.Char(string="Titulo")
    as_code = fields.Integer(string="Código")

class AsColor(models.Model):
    _name = "as.survey.color"
    _description = "Colores"

    name = fields.Char(string="Titulo")
    as_code = fields.Char(string="Codigo Hexadecimal")
    as_color = fields.Selection(
        [
            ('1','Azul'),
            ('2','Negrita'),
            ('3','Italica'),
            ('4','Rojo'),
            ('5','Gris'),
            ('6','Purpura'),
            ('7','Verde'),
            ('8','Marron'),

        ],
        string="Colores en las vistas",
    )

