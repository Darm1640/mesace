# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsTipoRetencion(models.Model):
    """Para almacenar los tipos de retencion para contabilidad en compras"""
    _inherit = 'as.tipo.retencion'
    
    as_taxes_ids = fields.Many2many('account.tax',string="Impuestos Relacionadas")
    as_extract_purchase = fields.Boolean(string="Extraer Impuestos a Compra")

class AsTipoRetencion(models.Model):
    """Para almacenar los tipos de retencion para contabilidad en compras"""
    _inherit = 'as.tipo.factura'
    
    as_taxes_ids = fields.Many2many('account.tax',string="Impuestos Relacionadas")
    as_extract_purchase = fields.Boolean(string="Extraer Impuestos a Compra")
