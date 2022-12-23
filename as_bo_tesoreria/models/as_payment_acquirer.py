# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class as_metodo_pago(models.Model):
    _name = 'as.payment.acquirer'
    _description="Tipo de pago o cobro"
    _order = 'tipo_documento'

    name = fields.Char('Nombre del método de pago', help=u'Nombre del método de pago.', required=True)
    account_id_ingreso = fields.Many2one('account.account', 'Cuenta de ingreso')
    account_id_egreso = fields.Many2one('account.account', 'Cuenta de egreso')
    tipo_documento = fields.Integer(string='Nro de documento', required=True, help='Tipo de documento para el auxiliar de ventas de bancarizacion')
    as_is_credito =  fields.Boolean(string="Es Tarjeta de Credito")
    as_is_debit =  fields.Boolean(string="Es Tarjeta de Debito")
    as_is_anticipo =  fields.Boolean(string="Es Pago contra anticipo")
    as_porcentaje = fields.Float(string='Comsión (%)')

    _sql_constraints = [('tipo_documento_uniq', 'unique (tipo_documento)', 'El Nro de documento Tienen que ser unico')
    ]