# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsTipoRetencion(models.Model):
    """Para almacenar los tipos de retencion para contabilidad en compras"""
    _inherit = 'as.tipo.factura'
    
    as_not_pay = fields.Boolean(string="Facturas Leasing")
    as_seg_anticipado = fields.Boolean(string="Facturas seguro anticipado")
