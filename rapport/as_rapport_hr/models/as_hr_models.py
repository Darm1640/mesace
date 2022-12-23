# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsSurveyPersonalidad(models.Model):
    _name = "as.personalidad"
    _description = "Evaluacion Consolidada"

    name= fields.Char(string="Nombre")

class AsCArgo(models.Model):
    _name = "as.cargo"
    _description = "Evaluacion Consolidada"

    name= fields.Char(string="Nombre")
