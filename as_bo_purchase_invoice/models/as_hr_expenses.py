# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
#Generacion del QR
import qrcode
import tempfile
import base64
#Convertir numeros en texto
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

tipo_de_compra = [
    ('1','Actividad gravada'),
    ('2','Actividad no gravada'),
    ('3','Sujetas a proporcionalidad'),
    ('4','Exportaciones'),
    ('5','Interno/Exportaciones')
]

class hr_expense(models.Model):
    _inherit = 'hr.expense'

    as_tipo_documento  = fields.Selection([('Factura','Factura'),('Prefactura/Recibo','Prefactura/Recibo')] ,'Tipo de documento', help=u'Tipo de documento que pertenece la factura.', default='Factura')
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion')
    as_tipo_factura  = fields.Many2one('as.tipo.factura','Tipo de Factura', help=u'Tipo de factura para el registro de libro de compra y calculo del monto exento automatico.')
    as_tipo_de_compra = fields.Selection(selection=tipo_de_compra, string="Tipo de compra", default='1',help="Tipo de compra para libro de compras Ejemplo:\n1: Actividad gravada \n2:Actividad no gravada \n3:Sujetas a proporcionalidad \n4:Exportaciones \n5:Interno/Exportaciones ")
    as_numero_factura_compra  = fields.Char(string='No Factura', help='Numero de factura.')
    as_codigo_control_compra = fields.Char('Codigo Control')
    as_numero_autorizacion_compra  = fields.Char(string='No Autorizacion', help='Numero de Autorizacion.', digits=(15, 0))
    as_monto_exento = fields.Float('Monto Exento.',store=True, readonly=True, compute='_compute_tipo_factura', help=u'factor de descuento total por monto excento de tipo de de factura de compra.')
    as_factor = fields.Float(related="as_tipo_factura.as_factor", store=True, string='Factor %')
    as_pagado = fields.Float('Pagos', help=u'Pagos que se tiene de la factura.')
    as_saldo = fields.Float('Saldo', help=u'Saldo que se tiene de la factura.')
    as_cuenta_gasto = fields.Many2one('account.account', string="Cuenta de gasto") # Tiene que ser obligatorio.
    # Lector Codigo QR
    as_scan_qr = fields.Char(string="QR factura", help="Click aqui para que el cursor lea el codigo de QR de la factura de compra")
    as_plazo = fields.Integer(string="Nro cuotas", readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    as_fecha_plan = fields.Date(string="Fecha", readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    as_payment_teas_id = fields.Many2one('account.payment.term', string="Plazo de pago")
    as_impuesto_especifico = fields.Float(string='ICE / IEHD', default=0.0)
    # as_costo_cero = fields.Boolean(string='Tasa en Cero', default=False)
    # as_iva = fields.Boolean(string='IVA', default=False)
    as_numero_dui = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.')