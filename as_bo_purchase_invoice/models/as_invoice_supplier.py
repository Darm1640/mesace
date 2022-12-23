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
import time
from time import mktime
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
class AccountInvoice(models.Model):
    """ Esta clase agrega los siguientes campos a la tabla account move """
    _inherit = 'account.move'

    date_invoice = fields.Date(string='Invoice Date',
        readonly=False, index=True,
        help="Keep empty to use the current date", copy=False)
    reference = fields.Char(string='Payment Ref.', copy=False, readonly=False,
        help='The payment communication that will be automatically populated once the invoice validation. You can also write a free communication.')

    def _obtener_total_descuento(self,invoice_id):
        invoices_line = self.env['account.move.line'].sudo().search([('move_id', '=', invoice_id)])
        monto=0.00
        monto_discount=0.00
        currency_company = self.company_id.currency_id
        for line in invoices_line:
            if line.discount > 0.00:
                price_unit = self.currency_id._convert(line.price_unit,currency_company,self.company_id, self.invoice_date,round=False)
                monto = (price_unit * line.quantity)
                monto_discount += (monto*line.discount)/100
        return monto_discount

    # @api.model
    # def invoice_line_move_line_get(self):
    #     res = super(AccountInvoice, self).invoice_line_move_line_get()
    #     monto_it=0.0
    #     if self.type != 'out_invoice':
    #         if self.as_tipo_factura.as_account:
    #             for item in res:
    #                 monto_it = (item['price']*(self.as_tipo_factura.as_iva_monto/100))
    #                 item['price'] = item['price'] - monto_it
    #                 item['price_unit'] = item['price_unit'] - monto_it
    #         if self.as_tipo_factura.as_calcular or self.as_tipo_factura.as_calcular_monto:
    #             cantidad = len(self.invoice_line_ids)
    #             for item in res:
    #                 if cantidad > 0:
    #                     monto=self.amount_total
    #                     ice = self.as_impuesto_especifico
    #                     monto_it = (monto-ice)*(self.as_tipo_factura.as_iva_monto/100)
    #                 else:
    #                     monto_it = 0.0
    #                 item['price'] = (monto - monto_it)/cantidad
    #                 item['price_unit'] = (monto - monto_it)/cantidad        
      
    #     return res
        
    # @api.model
    # def tax_line_move_line_get(self):
    #     if not self.as_tipo_factura.as_account and not self.as_tipo_factura.as_calcular and not self.as_tipo_factura.as_calcular_monto:
    #         res = super(AccountInvoice, self).tax_line_move_line_get()
    #     else:
    #         res = self.tax_line_move_line_get_line()
    #     return res

    # @api.model
    # def tax_line_move_line_get_line(self):
    #     res = []
    #     # keep track of taxes already processed
    #     done_taxes = []
    #     # loop the invoice.tax.line in reversal sequence
    #     if self.type != 'out_invoice':
    #         for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
    #             if tax_line.amount_total:
    #                 tax = tax_line.tax_id
    #                 if tax.amount_type == "group":
    #                     for child_tax in tax.children_tax_ids:
    #                         done_taxes.append(child_tax.id)
    #                 if self.as_tipo_factura.as_calcular or self.as_tipo_factura.as_calcular_monto:
    #                     monto = ((self.amount_total - self.as_impuesto_especifico)*13)/100
    #                 else:
    #                     monto = tax_line.amount_total
    #                 analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in tax_line.analytic_tag_ids]
    #                 res.append({
    #                     'invoice_tax_line_id': tax_line.id,
    #                     'tax_line_id': tax_line.tax_id.id,
    #                     'type': 'tax',
    #                     'name': tax_line.name,
    #                     'price_unit': monto,
    #                     'quantity': 1,
    #                     'price': monto,
    #                     'account_id': tax_line.account_id.id,
    #                     'account_analytic_id': tax_line.account_analytic_id.id,
    #                     'analytic_tag_ids': analytic_tag_ids,
    #                     'invoice_id': self.id,
    #                     'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
    #                 })
    #                 done_taxes.append(tax.id)
    #         if self.as_tipo_factura.as_account:
    #             monto_it = (self.amount_total*(self.as_tipo_factura.as_factor/100))
    #             move_line_dict = {
    #                 'type': 'tax',
    #                 'name':self.as_tipo_factura.name,
    #                 'price_unit':  round(monto_it,2),
    #                 'quantity': 1,
    #                 'price': round(monto_it,2),
    #                 'account_id': self.as_tipo_factura.as_account.id,
    #                 'invoice_id': self.id,
    #                 }
    #             res.append(move_line_dict)
    #     else:
    #         res+=self.tax_more_line_move_line_get()
    #         res+=self.tax_positive_line_move_line_get()
    #     return res

    """ Se formatea el campo codigo de control"""
    @api.onchange('as_codigo_control_compra')
    def change_as_codigo_control_compra(self):
        cont=0
        if self.as_codigo_control_compra:
            codigo=self.as_codigo_control_compra
            codigo= codigo.replace('-','')
            codigo= codigo.replace("'",'')
            self.as_codigo_control_compra = ''
            if len(codigo) > 10:
                raise UserError(_("No puede exceder los 5 pares de caracteres permitidos"))
            else:
                permitidos = ('ABCDEF0123456789')
                for char in codigo.upper():
                    if char not in permitidos: 
                        raise UserError(_("No puede se permiten letras diferentes a de A-F ni caracteres extras a numeros"))
                    else:
                        cont+=1
                        if (cont % 2)==0: 
                            if cont >= len(codigo):
                                self.as_codigo_control_compra += char
                            else:
                                self.as_codigo_control_compra += char + '-'
                        else:
                            self.as_codigo_control_compra += char

    """ Monto de acuerdo al tipo de factura """
    @api.depends('as_tipo_factura','amount_total')
    def _compute_tipo_factura(self):
        for invoice in self:
            monto = 0.0
            if invoice.as_tipo_factura:
                monto = invoice.amount_total * ((invoice.as_tipo_factura.as_factor or 0)/100.0)
            invoice.update({'as_monto_exento' : monto})
            
    tipo_de_compra = [
        ('1','Actividad gravada'),
        ('2','Actividad no gravada'),
        ('3','Sujetas a proporcionalidad'),
        ('4','Exportaciones'),
        ('5','Interno/Exportaciones')
    ]

    """ Cambia la razon social por lo que contiene bussines name """
    @api.onchange('partner_id')
    def change_razon_social_nit(self):
        last_purchase= self.env['purchase.order'].search([],order='create_date desc', limit=1)
        if self.partner_id:
            self.as_nit = self.partner_id.vat or 'S/N'
            self.as_razon_social = self.partner_id.as_razon_social or 'S/R'
            # if last_purchase:
            #     self.as_numero_autorizacion_compra = last_purchase.as_numero_autorizacion_compra or ''
                
    as_tipo_documento  = fields.Selection([('Factura','Factura'),('Prefactura/Recibo','Prefactura/Recibo')] ,'Tipo de documento', help=u'Tipo de documento que pertenece la factura.', default='Factura')
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion')
    as_tipo_factura  = fields.Many2one('as.tipo.factura','Tipo de Factura', help=u'Tipo de factura para el registro de libro de compra y calculo del monto exento automatico.')
    as_tipo_de_compra = fields.Selection(selection=tipo_de_compra, string="Tipo de compra", default='1',help="Tipo de compra para libro de compras Ejemplo:\n1: Actividad gravada \n2:Actividad no gravada \n3:Sujetas a proporcionalidad \n4:Exportaciones \n5:Interno/Exportaciones ") # Campo que es remplazado por as_tipo_compra
    as_tipo_compra = fields.Many2one('as.tipo.compra',string='Tipo de compra')
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
    as_impuesto_especifico = fields.Float(string='Otro no sujeto a credito fiscal', default=0.0)
    # as_costo_cero = fields.Boolean(string='Tasa en Cero', default=False)
    # as_iva = fields.Boolean(string='IVA', default=False)
    as_numero_dui = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.')

    as_importe_ic = fields.Float(string='Importe ICE ', default=0.0)
    as_importe_iehd = fields.Float(string='Importe IEHD ', default=0.0)
    as_importe_ipj = fields.Float(string='Importe IPJ ', default=0.0)
    as_tasas = fields.Float(string='Tasas ', default=0.0)
    as_interes = fields.Float(string='Intereses ', default=0.0)
    as_journal_aux = fields.Many2one('account.journal', string="Diario Auxiliar")
    as_exentos = fields.Float(string='Importes exentos', default=0.0)
    as_gift_card = fields.Float(string='Importes Gift Card', default=0.0)
    as_compras_gravadas = fields.Float(string='Importe compras gravadas a tasa cero', default=0.0)

    _sql_constraints = [('numero_autorizacion_uniq', 'unique (as_numero_factura_compra, as_numero_autorizacion_compra, partner_id, as_numero_dui,name)', 'El numero de autorizacion y No Factura tiene que ser Unico'),
		('number_uniq', 'Check(1=1)', 'Numero factura de compra unico por No de autorizacion!'),
	]

    @api.onchange('as_tipo_factura')
    def onchange_as_tipo_factura(self):  
        if self.as_tipo_factura.as_calcular: 
            self.as_impuesto_especifico =  (self.amount_total*(self.as_tipo_factura.as_factor/100))

    """ Funcion de escanear qr """
    @api.onchange('as_scan_qr')
    def escanear_codigo_qr(self):
        if self.as_scan_qr:
            array = (self.as_scan_qr).split(']')
            if len(array) != 12:
                raise UserError(_("Formato de QR invalido"))
            self.as_nit = array[0]
            self.as_numero_factura_compra = str(int(array[1]))
            self.as_numero_autorizacion_compra = array[2]
            fecha = array[3].split("-")
            self.invoice_date = fecha[2] +"-"+ fecha[1] + "-" + fecha[0]
            self.as_codigo_control_compra = array[6]
            self.as_codigo_control_compra = self.as_codigo_control_compra.replace("'",'-')
            self.as_tasas = array[8]
            self.as_compras_gravadas = array[9]
            self.as_scan_qr = None
            
    # """ Funcion para cambiar numero """
    # @api.onchange('as_numero_factura_compra','reference')
    # def cambiar_numero(self):
    #     for invoice in self:
    #         invoice.number = self.as_numero_factura_compra if self.as_numero_factura_compra else self.reference

    # """ Trae datos de la orden al seleccionarla """
    # @api.onchange('purchase_id')
    # def purchase_order_change(self):
    #     res = super(AccountInvoice,self).purchase_order_change()
    #     purchase_ids = self.invoice_line_ids.mapped('purchase_id')
    #     if purchase_ids:
    #         if len(purchase_ids) == 1:
    #             self.date_invoice = str(purchase_ids.as_fecha_factura)
    #             self.as_tipo_documento = purchase_ids.as_tipo_documento
    #             self.as_nit = purchase_ids.as_nit_compra
    #             self.razon_social = purchase_ids.as_razon_social_compra
    #             self.as_numero_factura_compra = purchase_ids.as_numero_factura_compra
    #             self.as_codigo_control_compra = purchase_ids.as_codigo_control_compra
    #             self.as_numero_autorizacion_compra = purchase_ids.as_numero_autorizacion_compra
    #             self.as_tipo_factura = purchase_ids.as_tipo_factura
    #             self.as_tipo_de_compra = purchase_ids.as_tipo_de_compra

    #     return res
