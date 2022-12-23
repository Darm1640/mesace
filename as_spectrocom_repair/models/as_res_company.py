# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from odoo.exceptions import UserError, ValidationError
class as_res_company(models.Model):
    _inherit = 'res.company'
    
    as_representante = fields.Char(string="Representante Legal")
    as_ci_company = fields.Char(string="Cedula de Identidad")
    as_nro_empleador_min_trabajo= fields.Char(string="Nº Empleador Min. Trabajo")