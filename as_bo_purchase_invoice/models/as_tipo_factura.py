# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class as_tipo_factura(models.Model):
    """Se agrega el modelo as_tipo_factura """
    _name = 'as.tipo.factura'
    _description = "Tipo de facturas de compras"
    _rec_name = 'name'

    name = fields.Char('Nombre', help=u'Nombre del tipo de factura.', required=True)
    as_factor = fields.Float(string="Factor %", required=True)
    as_costo_cero = fields.Boolean(string='Tasa en Cero', default=False)
    as_iva = fields.Boolean(string='IVA', default=False)   
    as_account = fields.Many2one('account.account', string="Cuenta de Iva no compensable")
    as_calcular = fields.Boolean(string='Calcular ICE/IHD por %', default=False)   
    as_calcular_monto = fields.Boolean(string='Calcular ICE/IHD por Monto', default=False)   
    as_iva_monto = fields.Float(string="IVA % para monto sustituido")
    as_no_participa = fields.Boolean(string="No participa en la distribucion de Gastos")