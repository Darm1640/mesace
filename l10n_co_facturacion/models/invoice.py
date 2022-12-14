# -*- coding: utf-8 -*-
import json
import datetime
from datetime import timedelta, date
import hashlib
import logging
import os
import pyqrcode
import zipfile
import pytz
import time

from .amount_to_txt_es import amount_to_text_es
from .signature import *
from enum import Enum
from jinja2 import Template
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import models, fields, api, _
from odoo.tools.misc import get_lang
from lxml import etree
from xml.sax import saxutils
from .helpers import WsdlQueryHelper

_logger = logging.getLogger(__name__)
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.ERROR)



class ConfigFE(Enum):
    company_postal = 'company_postal'
    company_pais = 'company_pais'
    company_ciudad = 'company_ciudad'
    company_departamento = 'company_departamento'
    company_direccion = 'company_direccion'
    company_nit = 'company_nit'
    company_digito_verificacion = 'company_digito_verificacion'
    company_tipo_documento = 'company_tipo_documento'
    company_email_from = 'company_email_from'
    company_tipo_regimen = 'company_tipo_regimen'
    company_telefono = 'company_telefono'
    company_matricula_mercantil = 'company_matricula_mercantil'
    company_responsabilidad_fiscal = 'company_responsabilidad_fiscal'
    company_responsabilidad_tributaria = 'company_responsabilidad_tributaria'

    tercero_es_compania = 'tercero_es_compania'
    tercero_postal = 'tercero_postal'
    tercero_pais = 'tercero_pais'
    tercero_ciudad = 'tercero_ciudad'
    tercero_departamento = 'tercero_departamento'
    tercero_direccion = 'tercero_direccion'
    tercero_razon_social = 'tercero_razon_social'
    tercero_primer_apellido = 'tercero_primer_apellido'
    tercero_segundo_apellido = 'tercero_segundo_apellido'
    tercero_primer_nombre = 'tercero_primer_nombre'
    tercero_segundo_nombre = 'tercero_segundo_nombre'
    tercero_nit = 'tercero_nit'
    tercero_digito_verificacion = 'tercero_digito_verificacion'
    tercero_tipo_documento = 'tercero_tipo_documento'
    tercero_to_email = 'tercero_to_email'
    tercero_tipo_regimen = 'tercero_tipo_regimen'
    tercero_telefono = 'tercero_telefono'
    tercero_matricula_mercantil = 'tercero_matricula_mercantil'
    tercero_responsabilidad_fiscal = 'tercero_responsabilidad_fiscal'
    tercero_responsabilidad_tributaria = 'tercero_responsabilidad_tributaria'

    padre_tercero_es_compania = 'padre_tercero_es_compania'
    padre_tercero_postal = 'padre_tercero_postal'
    padre_tercero_pais = 'padre_tercero_pais'
    padre_tercero_ciudad = 'padre_tercero_ciudad'
    padre_tercero_departamento = 'padre_tercero_departamento'
    padre_tercero_direccion = 'padre_tercero_direccion'
    padre_tercero_razon_social = 'padre_tercero_razon_social'
    padre_tercero_primer_apellido = 'padre_tercero_primer_apellido'
    padre_tercero_segundo_apellido = 'padre_tercero_segundo_apellido'
    padre_tercero_primer_nombre = 'padre_tercero_primer_nombre'
    padre_tercero_segundo_nombre = 'padre_tercero_segundo_nombre'
    padre_tercero_nit = 'padre_tercero_nit'
    padre_tercero_digito_verificacion = 'padre_tercero_digito_verificacion'
    padre_tercero_tipo_documento = 'padre_tercero_tipo_documento'
    padre_tercero_to_email = 'padre_tercero_to_email'
    padre_tercero_tipo_regimen = 'padre_tercero_tipo_regimen'
    padre_tercero_telefono = 'padre_tercero_telefono'
    padre_tercero_matricula_mercantil = 'padre_tercero_matricula_mercantil'
    padre_tercero_responsabilidad_fiscal = 'padre_tercero_responsabilidad_fiscal'
    padre_tercero_responsabilidad_tributaria = 'padre_tercero_responsabilidad_tributaria'

    sucursal_postal = 'sucursal_postal'
    sucursal_pais = 'sucursal_pais'
    sucursal_ciudad = 'sucursal_ciudad'
    sucursal_departamento = 'sucursal_departamento'
    sucursal_direccion = 'sucursal_direccion'
    sucursal_to_email = 'sucursal_to_email'
    sucursal_telefono = 'sucursal_telefono'

class Invoice(models.Model):
    _inherit = "account.move"

    
    fe_company = None
    fe_tercero = None
    parent_fe_tercero = None
    fe_sucursal_data = None

    usa_aiu = fields.Boolean(
        default=False,
        string='Factura de AIU'
    )

    pct_administracion = fields.Float(
        string='Administracion %',
    )
    pct_imprevistos = fields.Float(
        string='Imprevistos %',
    )
    pct_utilidad = fields.Float(
        string='Utilidad %',
    )

    objeto_contrato = fields.Char(string='Objeto contrato')

    numero_factura_origen =  fields.Char(string='Numero factura origen')
    cufe_factura_origen =  fields.Char(string='CUFE factura origen')
    fecha_factura_origen  = fields.Date(string='Fecha factura origen',copy=False)

    company_resolucion_id = fields.Many2one(
        'l10n_co_factura.company_resolucion',
        string='Resoluci??n',
        ondelete='set null',
        required=False,
        copy=False
    )
    envio_fe_id = fields.Many2one(
        'l10n_co_factura.envio_fe',
        string='Env??o Factura',
        copy=False
    )
    consecutivo_envio = fields.Integer(
        string='Consecutivo env??o',
        ondelete='set null',
        copy=False
    )
    filename_send_acknowledgement_electronic_invoice = fields.Char(string="nombre del archivo")
    filename_electronic_sales_invoice_claim = fields.Char(string="nombre del archivo")
    filename_refacturapt_services = fields.Char(string="nombre del archivo")
    filename_express_acceptance = fields.Char(string="nombre del archivo")
    email_send_acknowledgement_electronic_invoice = fields.Boolean(string="Email enviado")
    email_electronic_sales_invoice_claim = fields.Boolean(string="Email enviado")
    email_refacturapt_services = fields.Boolean(string="Email enviado")
    email_express_acceptance = fields.Boolean(string="Email enviado")
    attachment_id_send_acknowledgement_electronic_invoice = fields.Many2one(
        'ir.attachment',
        string='Archivo Adjunto',
        copy=False, tracking=True
    )
    attachment_id_electronic_sales_invoice_claim = fields.Many2one(
        'ir.attachment',
        string='Archivo Adjunto',
        copy=False, tracking=True
    )
    attachment_id_refacturapt_services = fields.Many2one(
        'ir.attachment',
        string='Archivo Adjunto',
        copy=False, tracking=True
    )
    attachment_id_express_acceptance = fields.Many2one(
        'ir.attachment',
        string='Archivo Adjunto',
        copy=False, tracking=True
    )
    attachment_id_tacit_acceptance = fields.Many2one(
        'ir.attachment',
        string='Archivo Adjunto',
        copy=False, tracking=True
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Archivo Adjunto',
        copy=False
    )
    nonce = fields.Char(
        string='Nonce',
        copy=False
    )
    fecha_envio = fields.Datetime(
        string='Fecha de env??o en UTC',
        copy=False
    )
    fecha_entrega = fields.Datetime(
        string='Fecha de entrega',
        copy=False
    )
    filename = fields.Char(
        string='Nombre de Archivo',
        copy=False
    )
    file = fields.Binary(
        string='Archivo',
        copy=False,
        attachment=False
    )

    file_send_acknowledgement_electronic_invoice = fields.Binary(
        string='Archivo',
        copy=False,
        attachment=False, tracking=True
    )
    file_electronic_sales_invoice_claim = fields.Binary(
        string='Archivo',
        copy=False,
        attachment=False, tracking=True
    )

    file_refacturapt_services = fields.Binary(
        string='Archivo',
        copy=False,
        attachment=False, tracking=True
    )
    file_express_acceptance = fields.Binary(
        string='Archivo',
        copy=False,
        attachment=False, tracking=True
    )

    file_tacit_acceptance = fields.Binary(
        string='Archivo',
        copy=False,
        attachment=False, tracking=True
    )

    answer_send_acknowledgement_electronic_invoice = fields.Char(string='Respuesta Dian',copy=False, tracking=True)
    answer_electronic_sales_invoice_claim = fields.Char(string='Respuesta Dian',copy=False, tracking=True)
    answer_refacturapt_services = fields.Char(string='Respuesta Dian',copy=False, tracking=True)
    answer_express_acceptance = fields.Char(string='Respuesta Dian',copy=False, tracking=True)
    answer_tacit_acceptance = fields.Char(string='Respuesta Dian',copy=False, tracking=True)

    attachment_file = fields.Binary(
        string='Archivo Attachment',
        copy=False,
        attachment=False
    )
    zipped_file = fields.Binary(
        string='Archivo Compreso',
        copy=False
    )
    firmado = fields.Boolean(
        string="??Est?? firmado?",
        default=False,
        copy=False
    )
    enviada = fields.Boolean(
        string="Enviada",
        default=False,
        copy=False
    )
    enviada_error = fields.Boolean(
        string="Correo de Error Enviado",
        default=False,
        copy=False
    )
    cufe_seed = fields.Char(
        string='CUFE seed',
        copy=False
    )
    cufe = fields.Char(
        string='CUFE',
        copy=False
    )
    qr_code = fields.Binary(
        string='C??digo QR',
        copy=False
    )

    fe_company_nit = fields.Char(
        string='NIT Compa????a',
       # compute='compute_fe_company_nit',
        store=False,
        copy=False
    )
    fe_tercero_nit = fields.Char(
        string='NIT Tercero',
        #compute='compute_fe_tercero_nit',
        store=False,
        copy=False
    )

    fe_company_digito_verificacion = fields.Char(
        string='Dig??to Verificaci??n Compa????a',
        #compute='compute_fe_company_digito_verificacion',
        store=False,
        copy=False
    )

    amount_total_text = fields.Char(
        #compute='_amount_int_text',
        copy=False
    )

    amount_total_text_cent = fields.Char(
        #compute='_amount_int_text',
        copy=False
    )

    fe_approved = fields.Selection(
        selection = [
            ('sin-calificacion', 'Sin calificar'),
            ('aprobada', 'Aprobada'),
            ('aprobada_sistema', 'Aprobada por el Sistema'),
            ('rechazada', 'Rechazada')]
        ,
        string='Respuesta Cliente',
        default='',
        copy=False
    )
    fe_feedback = fields.Text(
        string='Motivo del rechazo',
        copy=False
    )
    fe_company_email_from = fields.Text(
        string='Email de salida para facturaci??n electr??nica',
        #compute='compute_fe_company_email_from',
        store=False,
        copy=False
    )
    fe_tercero_to_email = fields.Text(
        string='Email del tercero para facturaci??n electr??nica',
        #compute='compute_fe_tercero_to_email',
        store=False,
        copy=False
    )
    access_token = fields.Char(
        string='Access Token',
        copy=False
    )

    tipo_resolucion = fields.Selection(
        related="company_resolucion_id.tipo",
        string="Tipo de Resoluci??n",
        copy=False
    )

    tipo_resolucion_diario_f = fields.Selection(
        related="journal_id.company_resolucion_factura_id.tipo",
        string="Tipo de Resoluci??n Factura",
        copy=False
    )

    tipo_resolucion_diario_n = fields.Selection(
        related="journal_id.company_resolucion_credito_id.tipo",
        string="Tipo de Resoluci??n Nota Credito",
        copy=False
    )

    estado_dian = fields.Text(
        related="envio_fe_id.respuesta_validacion",
        copy=False
    )

    # Establece por defecto el medio de pago Efectivo
    payment_mean_id = fields.Many2one(
        'l10n_co_factura.payment_mean',
        string='Medio de pago',
        copy=False,
        default=lambda self: self.env['l10n_co_factura.payment_mean'].sudo().search([('codigo_fe_dian', '=', '10')], limit=1)
    )

    forma_de_pago = fields.Selection(
        selection = [
            ('1', 'Contado'),
            ('2', 'Cr??dito'),
        ],
        string='Forma de pago',
        default='1'
    )

    enviada_por_correo = fields.Boolean(
        string='??Enviada al cliente?',
        copy=False
    )

    concepto_correccion_credito = fields.Selection(
        selection=[
            ('1', 'Devoluci??n parcial de los bienes y/o no aceptaci??n parcial del servicio'),
            ('2', 'Anulaci??n de factura electr??nica'),
            ('3', 'Rebaja o descuento parcial o total'),
            ('4', 'Ajuste de precio'),
            ('5', 'Otros')
        ],
        string='Concepto  de  correcci??n',
        default='2'
    )

    concepto_correccion_debito = fields.Selection(
        selection=[
            ('1', 'Intereses'),
            ('2', 'Gastos por cobrar'),
            ('3', 'Cambio del valor'),
            ('4', 'Otro')
        ]
    )

    es_nota_debito = fields.Boolean(
        string='??Es una nota d??bito?'
    )

    credited_invoice_id = fields.Many2one(
        'account.move',
        string='Factura origen',
        copy=False
    )

    es_factura_exportacion = fields.Boolean(
        string='Factura de exportaci??n'
    )

    es_factura_electronica = fields.Boolean(
        string='Es una factura electr??nica'
    )

    fe_habilitar_facturacion_related = fields.Boolean(
        string='Habilitar Facturaci??n electr??nica',
        compute='compute_fe_habilitar_facturacion_related'
    )
    fe_archivos_email = fields.One2many(
        'l10n_co_factura.fe_archivos_email',
        'invoice_id',
        string='Archivos adjuntos',
        copy=False
    )

    fe_sucursal = fields.Many2one(
        'res.partner',
        string='Sucursal Facturaci??n',
    )

    company_partner_id = fields.Many2one(
        'res.partner',
       # compute='compute_company_partner_id',
        string='Partner ID'
    )

    fe_habilitada_compania = fields.Boolean(
        string='FE Compa????a',
        #compute='compute_fe_habilitada_compania',
        store=False,
        copy=False
    )

    enable_invoice_discount = fields.Selection(
        selection=[
            ('value', 'Por Valor'),
            ('percent', 'Por Porcentaje'),
        ],
        string='Descuento Pie de Factura',
        default=''
    )

    invoice_discount = fields.Monetary(
        string='Desc. De Factura $',
    )

    invoice_discount_view = fields.Monetary(
        related="invoice_discount",
        string='Desc. De Factura',
        store=False
    )

    invoice_discount_percent = fields.Float(
        string='Desc. De Factura %',
    )

    invoice_discount_text = fields.Selection(
        selection=[
            ('00', 'Descuento no condicionado'),
            ('01', 'Descuento condicionado')
        ],
        string='Motivo de Descuento',
    )
    invoice_charges_freight = fields.Monetary(
        string='Cargo de Factura $',
    )
    invoice_charges_freight_percent = fields.Float(
        string='Cargo de Factura %',
    )
    invoice_charges_freight_view = fields.Monetary(
        related="invoice_charges_freight",
        string='Cargo De Factura',
        store=False
    )
    invoice_charges_freight_text = fields.Char(
        string='Motivo de Flete',
    )
    total_withholding_amount = fields.Float(
        string='Total de retenciones'
    )
    fecha_xml = fields.Datetime(
        string='Fecha de factura Publicada',
        copy=False
    )
    invoice_trade_sample = fields.Boolean(
        string='Tiene muestras comerciales',
    )
    trade_sample_price = fields.Selection(
        [
            ('01', 'Valor comercial')
        ],
        string='Referencia a precio real',
    )
    invoice_discount_base = fields.Boolean(
        string='Descuento calculado sobre el subtotal de la factura',
        help='Si se selecciona el porcentaje de descuento por pie de factura se aplicar?? sobre el subtotal de la factura, de lo contrario se aplicar?? sobre el valor a pagar (subtotal+impuestos)'
    )
    order_reference = fields.Char(string='Orden de compra ')

    order_reference_date = fields.Date(string= 'Fecha de orden de compra')
    additional_document_reference = fields.Char(string='Referencia de documento')
    despatch_document_reference = fields.Char(string='Orden de despacho')
    despatch_document_reference_date = fields.Date(string='Fecha de orden de despacho')
    refacturapt_document_reference = fields.Char(string='Hoja de entrada de servicio')
    refacturapt_document_reference_date = fields.Date(string='Fecha de hoja de entrada de servicio')

    pre_payment_line_ids = fields.Many2many('account.move.line',relation='account_move_account_move_line_rel',column1='account_move_id',column2='account_move_line_id',column3='aporte', string='Pagos previos')
    subtotal_pendiente_pago=fields.Float("Valor pendiente pago",)

    category_resolution_dian_id = fields.Many2one(
        'l10n_co_factura.category_resolution',
        string='Tipo De Categoria de Resoluci??n Dian'
    )

    application_response_cude = fields.Char(string="CUDE ApplicationResponse", tracking=True)

    supplier_invoice_cufe = fields.Char(string="CUFE Factura Proveedor", tracking=True)

    supplier_invoice_type = fields.Selection(
        [
            ('01', 'Factura electr??nica de venta'),
            ('03', 'Instrumento electr??nico de transmisi??n ??? tipo 03'),
            ('04', 'Factura electr??nica de Venta ??? tipo 04'),
            ('91', 'Nota Cr??dito'),
            ('92', 'Nota D??bito'),
        ],
        string="Tipo factura proveedor", tracking=True)

    supplier_claim_concept = fields.Selection(
        [
            ('01', 'Documento con inconsistencias'),
            ('02', 'Mercanc??a no entregada totalmente'),
            ('03', 'Mercanc??a no entregada parcialmente'),
            ('04', 'Servicio no prestado'),
        ],
        string="Concepto de Reclamo", tracking=True)

    invoice_mandate_contract = fields.Boolean(string="Factura contrato por mandato", tracking=True)

    mandate_id = fields.Many2one('res.partner', string="Mandatorio", tracking=True)

    customer_invoice_type = fields.Selection(
        [
            ('01', 'Factura electr??nica de venta'),
            ('03', 'Instrumento electr??nico de transmisi??n ??? tipo 03'),
            ('04', 'Factura electr??nica de Venta ??? tipo 04'),
            ('91', 'Nota Cr??dito'),
            ('92', 'Nota D??bito'),
        ],
        string="Tipo factura cliente", tracking=True)

    # #endregion
    # #region _compute_valor_pendiente_pago
    # @api.depends('pre_payment_line_ids')
    # def _compute_valor_pendiente_pago(self):
    #     for move in self:
    #         #print("Esto debe ser puesto para hacer el pull ")
    #         move.subtotal_pendiente_pago = move.amount_total
    #         for line in move.pre_payment_line_ids:
    #             descontar=0
    #             if move.subtotal_pendiente_pago>0:
    #                 if move.subtotal_pendiente_pago>(-line.amount_residual):
    #                     descontar= (-line.amount_residual)
    #                 else:
    #                     descontar= move.subtotal_pendiente_pago
    #                 move.subtotal_pendiente_pago -=descontar
    #             else:
    #                 move.pre_payment_line_ids=[(2,line.id)]
    # #endregion
    # #region borra_aiu
    # @api.onchange('usa_aiu')
    # def borra_aiu(self):
    #     self.ensure_one()
    #     if self.usa_aiu == False:
    #         producto_administracion = self.env['product.product'].sudo().search([('tipo_aiu', '=', 'administracion'),'|', ('company_id', '=', False),('company_id', '=', self.company_id.id)])
    #         producto_imprevistos = self.env['product.product'].sudo().search(
    #             [('tipo_aiu', '=', 'imprevistos'),'|', ('company_id', '=', False),('company_id', '=', self.company_id.id)])
    #         producto_utilidad = self.env['product.product'].sudo().search(
    #             [('tipo_aiu', '=', 'utilidad'),'|', ('company_id', '=', False),('company_id', '=', self.company_id.id)])
    #         productos_aiu = [producto_administracion.id, producto_imprevistos.id, producto_utilidad.id]

    #         for invoice in self:
    #             for line in invoice.line_ids:
    #                 if line.product_id.id in productos_aiu:
    #                     invoice.invoice_line_ids = [(2, line.id)]
    #         invoice._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
    # #endregion
    # #region calcular_aiu
    # @api.onchange('usa_aiu', 'pct_administracion', 'pct_imprevistos', 'pct_utilidad', 'invoice_line_ids')
    # def calcular_aiu(self):
    #     self.ensure_one()
    #     if self.usa_aiu == True:
    #         base_aiu = 0
    #         producto_administracion = self.env['product.product'].sudo().search([('tipo_aiu', '=', 'administracion'),'|', ('company_id', '=', False),('company_id', '=', self.company_id.id)])
    #         producto_imprevistos = self.env['product.product'].sudo().search(
    #             [('tipo_aiu', '=', 'imprevistos'),'|', ('company_id', '=', False),('company_id', '=', self.company_id.id)])
    #         producto_utilidad = self.env['product.product'].sudo().search(
    #             [('tipo_aiu', '=', 'utilidad'),'|', ('company_id', '=', False),('company_id', '=', self.company_id.id)])
    #         productos_aiu = [producto_administracion.id, producto_imprevistos.id, producto_utilidad.id]
    #         productos_aiu_used = []
    #         for invoice in self:
    #             for line in invoice.line_ids:
    #                 if line.product_id.id in productos_aiu:
    #                     productos_aiu_used.append(line.product_id.id)
    #                     # invoice.invoice_line_ids = [(2, line.id)]
    #                 elif not line.exclude_from_invoice_tab and not line.product_id.enable_charges:
    #                     base_aiu += line.price_subtotal
    #             if base_aiu != 0:
    #                 mapa_linea = {
    #                     'name': self.invoice_payment_ref or '',
    #                     'quantity': 1.0,
    #                     'amount_currency': 0,
    #                     'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
    #                     'partner_id': self.commercial_partner_id.id,
    #                     'exclude_from_invoice_tab': False,
    #                     'move_id': invoice.id
    #                 }
    #                 if self.pct_administracion > 0:
    #                     if not producto_administracion.id in productos_aiu_used:
    #                         invoice.invoice_line_ids = [(0, False, mapa_linea)]
    #                         line = invoice.invoice_line_ids[len(invoice.invoice_line_ids) - 1]
    #                         line.tax_ids = line._get_computed_taxes()
    #                     else:
    #                         for item in invoice.line_ids:
    #                             if item.product_id == producto_administracion:
    #                                 line = item
    #                                 line.write(mapa_linea)
    #                     line.quantity = 1
    #                     line.amount_currency = 0
    #                     line.currency_id = self.currency_id.id if self.currency_id != self.company_id.currency_id else False
    #                     line.partner_id = self.commercial_partner_id.id
    #                     line.product_id = producto_administracion
    #                     line.price_unit = base_aiu * self.pct_administracion / 100
    #                     line.name = line._get_computed_name()
    #                     line.account_id = line._get_computed_account()
    #                     line._onchange_mark_recompute_taxes()
    #                     line._set_price_and_tax_after_fpos()
    #                     line._onchange_price_subtotal()
    #                     line.product_uom_id = producto_administracion.product_tmpl_id.uom_id
    #                 else:
    #                     for item in invoice.line_ids:
    #                         if item.product_id == producto_administracion:
    #                             invoice.invoice_line_ids = [(2, item.id)]
    #                 if self.pct_imprevistos > 0:
    #                     if not producto_imprevistos.id in productos_aiu_used:
    #                         invoice.invoice_line_ids = [(0, False, mapa_linea)]
    #                         line = invoice.invoice_line_ids[len(invoice.invoice_line_ids) - 1]
    #                         line.tax_ids = line._get_computed_taxes()
    #                     else:
    #                         for item in invoice.line_ids:
    #                             if item.product_id == producto_imprevistos:
    #                                 line = item
    #                                 line.write(mapa_linea)
    #                     line.quantity = 1
    #                     line.amount_currency = 0
    #                     line.currency_id = self.currency_id.id if self.currency_id != self.company_id.currency_id else False
    #                     line.partner_id = self.commercial_partner_id.id
    #                     line.product_id = producto_imprevistos
    #                     line.price_unit = base_aiu * self.pct_imprevistos / 100
    #                     line.name = line._get_computed_name()
    #                     line.account_id = line._get_computed_account()
    #                     line._onchange_mark_recompute_taxes()
    #                     line._set_price_and_tax_after_fpos()
    #                     line._onchange_price_subtotal()
    #                     line.product_uom_id = producto_imprevistos.product_tmpl_id.uom_id
    #                 else:
    #                     for item in invoice.line_ids:
    #                         if item.product_id == producto_imprevistos:
    #                             invoice.invoice_line_ids = [(2, item.id)]
    #                 if self.pct_utilidad > 0:
    #                     if not producto_utilidad.id in productos_aiu_used:
    #                         invoice.invoice_line_ids = [(0, False, mapa_linea)]
    #                         line = invoice.invoice_line_ids[len(invoice.invoice_line_ids) - 1]
    #                         line.tax_ids = line._get_computed_taxes()
    #                     else:
    #                         for item in invoice.line_ids:
    #                             if item.product_id == producto_utilidad:
    #                                 line = item
    #                                 line.write(mapa_linea)
    #                     line.quantity = 1
    #                     line.amount_currency = 0
    #                     line.currency_id = self.currency_id.id if self.currency_id != self.company_id.currency_id else False
    #                     line.partner_id = self.commercial_partner_id.id
    #                     line.product_id = producto_utilidad
    #                     line.price_unit = base_aiu * self.pct_utilidad / 100
    #                     line.name = line._get_computed_name()
    #                     line.account_id = line._get_computed_account()
    #                     line._onchange_mark_recompute_taxes()
    #                     line._set_price_and_tax_after_fpos()
    #                     line._onchange_price_subtotal()
    #                     line.product_uom_id = producto_utilidad.product_tmpl_id.uom_id
    #                 else:
    #                     for item in invoice.line_ids:
    #                         if item.product_id == producto_utilidad:
    #                             invoice.invoice_line_ids = [(2, item.id)]
    #             else:
    #                 for line in invoice.line_ids:
    #                     invoice.invoice_line_ids = [(2, line.id)]
    #             invoice._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
    # #endregion
    # #region compute_fecha_entrega
    # # Fechas de Entrega
    # @api.onchange('invoice_date')
    # def compute_fecha_entrega(self):
    #     if self.invoice_date and not self.fecha_entrega:
    #         self.fecha_entrega = datetime.datetime.combine(self.invoice_date, datetime.datetime.now().time())
    #     if self.invoice_date and not self.fecha_xml:
    #         self.fecha_xml = datetime.datetime.combine(self.invoice_date, datetime.datetime.now().time())

    # def calcular_texto_descuento(self, id):
    #     if id == '00':
    #         return 'Descuento no condicionado'
    #     elif id == '01':
    #         return 'Descuento condicionado'
    #     else:
    #         return ''

    # def calcular_texto_responsabilidad_tributaria(self, id):
    #     if id == '01':
    #         return 'IVA'
    #     elif id == '04':
    #         return 'INC'
    #     elif id == 'ZA':
    #         return 'IVA e INC'
    #     elif id == 'ZZ':
    #         return 'No aplica'
    #     else:
    #         return ''

    # #endregion
    # #region compute_amount
    # # Funcion de odoo sobrecargada que auto calcula el total de la factura (se le agrego el descuento de factura para que realize el calculo total)

    # @api.depends(
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'invoice_discount',
    #     'invoice_discount_percent',
    #     'line_ids.payment_id.state')
    # def _compute_amount(self):
    #     invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_refacturapts=True)]
    #     self.env['account.payment'].flush(['state'])
    #     if invoice_ids:
    #         self._cr.execute(
    #             '''
    #                 SELECT move.id
    #                 FROM account_move move
    #                 JOIN account_move_line line ON line.move_id = move.id
    #                 JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
    #                 JOIN account_move_line rec_line ON
    #                     (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
    #                     OR
    #                     (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
    #                 JOIN account_payment payment ON payment.id = rec_line.payment_id
    #                 JOIN account_journal journal ON journal.id = rec_line.journal_id
    #                 WHERE payment.state IN ('posted', 'sent')
    #                 AND journal.post_at = 'bank_rec'
    #                 AND move.id IN %s
    #             ''', [tuple(invoice_ids)]
    #         )
    #         in_payment_set = set(res[0] for res in self._cr.fetchall())
    #     else:
    #         in_payment_set = {}

    #     for move in self:
    #         total_untaxed = 0.0
    #         total_untaxed_currency = 0.0
    #         total_tax = 0.0
    #         total_tax_currency = 0.0
    #         total_residual = 0.0
    #         total_residual_currency = 0.0
    #         total = 0.0
    #         total_currency = 0.0
    #         currencies = set()
    #         for line in move.line_ids:
    #             if move.move_type in ['in_invoice', 'in_refund'] or (not line.product_id.enable_charges and line.name!='Descuento A Total de Factura'):
    #                 if line.currency_id:
    #                     currencies.add(line.currency_id)

    #                 if move.is_invoice(include_refacturapts=True):
    #                     # === Invoices ===

    #                     if not line.exclude_from_invoice_tab:
    #                         # Untaxed amount.
    #                         total_untaxed += line.balance
    #                         total_untaxed_currency += line.amount_currency
    #                         total += line.balance
    #                         total_currency += line.amount_currency
    #                     elif line.tax_line_id:
    #                         # Tax amount.
    #                         total_tax += line.balance
    #                         total_tax_currency += line.amount_currency
    #                         total += line.balance
    #                         total_currency += line.amount_currency
    #                     elif line.account_id.user_type_id.type in ('refacturavable', 'payable'):
    #                         # Residual amount.
    #                         total_residual += line.amount_residual
    #                         total_residual_currency += line.amount_residual_currency
    #                 else:
    #                     # === Miscellaneous journal entry ===
    #                     if line.debit:
    #                         total += line.balance
    #                         total_currency += line.amount_currency
    #             elif move.move_type not in ['in_invoice', 'in_refund'] and (line.product_id.enable_charges or line.name=='Descuento A Total de Factura'):
    #                 total += line.balance
    #                 total_currency += line.amount_currency

    #         if move.move_type == 'entry' or move.is_outbound():
    #             sign = 1
    #         else:
    #             sign = -1


    #         move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
    #         move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
    #         move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
    #         move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
    #         move.amount_untaxed_signed = -total_untaxed
    #         move.amount_tax_signed = -total_tax
    #         move.amount_total_signed = -total
    #         move.amount_residual_signed = total_residual


    #         currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
    #         is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

    #         # Compute 'invoice_payment_state'.
    #         if move.state == 'posted' and is_paid:
    #             if move.id in in_payment_set:
    #                 move.invoice_payment_state = 'in_payment'
    #             else:
    #                 move.invoice_payment_state = 'paid'
    #         else:
    #             move.invoice_payment_state = 'not_paid'
    # # Fin de la Funcionalidad
    # #endregion
    # #region compute_amount_discount
    # def compute_amount_discount(self,values,val,other_currency):
    #     if self:
    #         for move in self:
    #             total_untaxed = 0.0
    #             total_untaxed_currency = 0.0
    #             total_tax = 0.0
    #             total_tax_currency = 0.0
    #             total_residual = 0.0
    #             total_residual_currency = 0.0
    #             total = 0.0
    #             total_currency = 0.0
    #             currencies = set()
    #             for line in move.line_ids:
    #                 if move.move_type in ['in_invoice', 'in_refund'] or (not line.product_id.enable_charges and line.name!='Descuento A Total de Factura'):
    #                     if line.currency_id:
    #                         currencies.add(line.currency_id)

    #                     if move.is_invoice(include_refacturapts=True):
    #                         # === Invoices ===

    #                         if not line.exclude_from_invoice_tab:
    #                             # Untaxed amount.
    #                             total_untaxed += line.balance
    #                             total_untaxed_currency += line.amount_currency
    #                             total += line.balance
    #                             total_currency += line.amount_currency
    #                         elif line.tax_line_id:
    #                             # Tax amount.
    #                             total_tax += line.balance
    #                             total_tax_currency += line.amount_currency
    #                             total += line.balance
    #                             total_currency += line.amount_currency
    #                         elif line.account_id.user_type_id.type in ('refacturavable', 'payable'):
    #                             # Residual amount.
    #                             total_residual += line.amount_residual
    #                             total_residual_currency += line.amount_residual_currency
    #                     else:
    #                         # === Miscellaneous journal entry ===
    #                         if line.debit:
    #                             total += line.balance
    #                             total_currency += line.amount_currency
    #                 elif move.move_type not in ['in_invoice', 'in_refund'] and (line.product_id.enable_charges or line.name=='Descuento A Total de Factura'):
    #                     total += line.balance
    #                     total_currency += line.amount_currency

    #             if move.move_type == 'entry' or move.is_outbound():
    #                 sign = 1
    #             else:
    #                 sign = -1


    #             move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
    #             move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
    #             move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
    #             move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
    #             move.amount_untaxed_signed = -total_untaxed
    #             move.amount_tax_signed = -total_tax
    #             move.amount_total_signed = -total
    #             move.amount_residual_signed = total_residual
    #     else:
    #         total_untaxed = 0.0
    #         total_untaxed_currency = 0.0
    #         total_tax = 0.0
    #         total_tax_currency = 0.0
    #         total_residual = 0.0
    #         total_residual_currency = 0.0
    #         total = 0.0
    #         total_currency = 0.0
    #         currencies = set()
    #         company_id = self.env.companies

    #         for lines in values['line_ids']:
    #             line=lines[2]
    #             product_id = company_id.env['product.product'].sudo().search([('id', '=', line['product_id'])])
    #             account_id = company_id.env['account.account'].sudo().search([('id', '=', line['account_id'])])
    #             if (not product_id.enable_charges and line['name'] != 'Descuento A Total de Factura'):
    #                 if line['currency_id']:
    #                     currencies.add(line['currency_id'])


    #                 if not line['exclude_from_invoice_tab']:
    #                     # Untaxed amount.
    #                     total_untaxed += -line['debit']+line['credit']
    #                     total_untaxed_currency += line['amount_currency']
    #                     total += -line['debit']+line['credit']
    #                     total_currency += line['amount_currency']
    #                 elif line['tax_base_amount']!=0:
    #                     # Tax amount.
    #                     total_tax += -line['debit']+line['credit']
    #                     total_tax_currency += line['amount_currency']
    #                     total += -line['debit']+line['credit']
    #                     total_currency += line['amount_currency']
    #                 '''elif account_id.user_type_id.type in ('refacturavable', 'payable'):
    #                     # Residual amount.
    #                     total_residual += line['amount_residual']
    #                     total_residual_currency += line['amount_residual_currency']'''
    #             elif (line['name'] == 'Descuento A Total de Factura'):
    #                 total += -line['debit']+line['credit']
    #                 total_currency += line['amount_currency']

    #         sign = -1

    #         amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
    #         amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
    #         amount_total = sign * (total_currency if len(currencies) == 1 else total)
    #         amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
    #         amount_untaxed_signed = -total_untaxed
    #         amount_tax_signed = -total_tax
    #         amount_total_signed = -total
    #         amount_residual_signed = total_residual
    #     if(val==True):
    #         if other_currency:
    #             return amount_untaxed_signed
    #         else:
    #             return amount_untaxed
    #     else:
    #         if other_currency:
    #             return amount_total_signed
    #         else:
    #             return amount_total
    # # Funcionalidad de agregar descuento para el asiento contable
    # #endregion
    # #region invoice_discount_get genera l??nea para los descuentos
    # def invoice_discount_get(self,sign,discount,values,line_exist=False):
    #     move_disc = {}
    #     other_currency=False
    #     if self.enable_invoice_discount or line_exist or ('invoice_discount' in values and values['invoice_discount']>0) or ('invoice_discount_percent' in values and values['invoice_discount_percent']):
    #         if self.enable_invoice_discount or line_exist:
    #             if not self.journal_id.default_credit_discount_id:
    #                 raise ValidationError("Defina en el diario una cuenta cr??dito para la aplicaci??n de Descuentos")
    #             if not self.journal_id.default_debit_discount_id:
    #                 raise ValidationError("Defina en el diario una cuenta d??bito para la aplicaci??n de Descuentos")
    #             if sign:
    #                 value = -self.invoice_discount
    #                 account=self.journal_id.default_credit_discount_id.id

    #             else:
    #                 value = -self.invoice_discount
    #                 account = self.journal_id.default_debit_discount_id.id

    #             currency_id=self.currency_id.id
    #             '''if type(self.id) != int:
    #                 move_id=self.id.origin
    #             else:
    #                 move_id=self.id'''
    #             if self.company_id.currency_id.id != currency_id:
    #                 other_currency=True

    #         else:
    #             journal_id=self.env['account.journal'].sudo().search([('id','=',values['journal_id'])])
    #             if not journal_id.default_credit_discount_id:
    #                 raise ValidationError("Defina en el diario una cuenta cr??dito para la aplicaci??n de Descuentos")
    #             if not journal_id.default_debit_discount_id:
    #                 raise ValidationError("Defina en el diario una cuenta d??bito para la aplicaci??n de Descuentos")
    #             if sign:
    #                 account = journal_id.default_credit_discount_id.id
    #                 value = discount

    #             else:
    #                 account = journal_id.default_debit_discount_id.id
    #                 value = -discount

    #             currency_id = values['currency_id']
    #             if journal_id.company_id.currency_id.id != currency_id:
    #                 other_currency=True
    #         if other_currency:
    #             move_disc = {
    #                 'name': 'Descuento A Total de Factura',
    #                 'price_unit': value,
    #                 'quantity': 1,
    #                 'price_subtotal': value,
    #                 'price_total': value,
    #                 'account_id': account,
    #                 'move_id': self.id,
    #                 'currency_id':currency_id,
    #                 'exclude_from_invoice_tab': True,
    #             }
    #         else:
    #             move_disc = {
    #                 'name': 'Descuento A Total de Factura',
    #                 'price_unit': value,
    #                 'quantity': 1,
    #                 'price_subtotal': value,
    #                 'price_total': value,
    #                 'account_id': account,
    #                 'move_id': self.id,
    #                 'exclude_from_invoice_tab': True,
    #             }

    #     return move_disc
    # # Fin de la funcionalidad
    # #endregion
    # #region _recompute_tax_lines
    # def _recompute_tax_lines(self, recompute_tax_base_amount=False):
    #     ''' Compute the dynamic tax lines of the journal entry.

    #     :param lines_map: The line_ids dispatched by type containing:
    #         * base_lines: The lines having a tax_ids set.
    #         * tax_lines: The lines having a tax_line_id set.
    #         * terms_lines: The lines generated by the payment terms of the invoice.
    #         * rounding_lines: The cash rounding lines of the invoice.
    #     '''
    #     self.ensure_one()
    #     in_draft_mode = self != self._origin

    #     def _serialize_tax_grouping_key(grouping_dict):
    #         ''' Serialize the dictionary values to be used in the taxes_map.
    #         :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
    #         :return: A string representing the values.
    #         '''
    #         return '-'.join(str(v) for v in grouping_dict.values())

    #     def _compute_base_line_taxes(base_line):
    #         ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
    #         amount_currency & balance could not be the same as the expected currency rate.
    #         The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
    #         :param base_line:   The account.move.line owning the taxes.
    #         :return:            The result of the compute_all method.
    #         '''
    #         move = base_line.move_id
    #         sign = -1 if move.is_inbound() else 1
    #         if move.is_invoice(include_refacturapts=True):
    #             handle_price_include = True

    #             quantity = base_line.quantity
    #             if base_line.currency_id:
    #                 price_unit_foreign_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
    #                 price_unit_comp_curr = base_line.currency_id._convert(price_unit_foreign_curr, move.company_id.currency_id, move.company_id, move.date)
    #             else:
    #                 price_unit_foreign_curr = 0.0
    #                 price_unit_comp_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
    #             tax_type = 'sale' if move.move_type.startswith('out_') else 'purchase'
    #             is_refund = move.move_type in ('out_refund', 'in_refund')
    #         else:
    #             handle_price_include = False
    #             quantity = 1.0
    #             price_unit_foreign_curr = base_line.amount_currency
    #             price_unit_comp_curr = base_line.balance
    #             tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
    #             is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
    #             #debito si funciona pero credito no
    #         if  (not move.is_invoice(include_refacturapts=True) and base_line.balance!=0) or (move.is_invoice(include_refacturapts=True) and base_line.price_unit!=0):
    #             balance_taxes_res = base_line.tax_ids._origin.compute_all(
    #                 price_unit_comp_curr,
    #                 currency=base_line.company_currency_id,
    #                 quantity=quantity,
    #                 product=base_line.product_id,
    #                 partner=base_line.partner_id,
    #                 is_refund=is_refund,
    #                 handle_price_include=handle_price_include,
    #             )
    #         else:
    #             balance_taxes_res = base_line.tax_ids._origin.compute_all(
    #                 (sign * base_line.line_price_reference),
    #                 currency=base_line.company_currency_id,
    #                 quantity=quantity,
    #                 product=base_line.product_id,
    #                 partner=base_line.partner_id,
    #                 is_refund=is_refund,
    #                 handle_price_include=handle_price_include,
    #             )
    #         if move.move_type == 'entry':
    #             repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
    #             repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
    #             tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
    #             if tags_need_inversion:
    #                 balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
    #                 for tax_res in balance_taxes_res['taxes']:
    #                     tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

    #         if base_line.currency_id:
    #             # Multi-currencies mode: Taxes are computed both in company's currency / foreign currency.
    #             amount_currency_taxes_res = base_line.tax_ids._origin.compute_all(
    #                 price_unit_foreign_curr,
    #                 currency=base_line.currency_id,
    #                 quantity=quantity,
    #                 product=base_line.product_id,
    #                 partner=base_line.partner_id,
    #                 is_refund=self.type in ('out_refund', 'in_refund'),
    #                 handle_price_include=handle_price_include,
    #             )

    #             if move.move_type == 'entry':
    #                 repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
    #                 repartition_tags = base_line.tax_ids.mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
    #                 tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
    #                 if tags_need_inversion:
    #                     balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
    #                     for tax_res in balance_taxes_res['taxes']:
    #                         tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

    #             for b_tax_res, ac_tax_res in zip(balance_taxes_res['taxes'], amount_currency_taxes_res['taxes']):
    #                 tax = self.env['account.tax'].browse(b_tax_res['id'])
    #                 b_tax_res['amount_currency'] = ac_tax_res['amount']

    #                 # A tax having a fixed amount must be converted into the company currency when dealing with a
    #                 # foreign currency.
    #                 if tax.amount_type == 'fixed':
    #                     b_tax_res['amount'] = base_line.currency_id._convert(b_tax_res['amount'], move.company_id.currency_id, move.company_id, move.date)

    #         return balance_taxes_res

    #     taxes_map = {}

    #     # ==== Add tax lines ====
    #     to_remove = self.env['account.move.line']
    #     for line in self.line_ids.filtered('tax_repartition_line_id'):
    #         grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
    #         grouping_key = _serialize_tax_grouping_key(grouping_dict)
    #         if grouping_key in taxes_map:
    #             # A line with the same key does already exist, we only need one
    #             # to modify it; we have to drop this one.
    #             to_remove += line
    #         else:
    #             taxes_map[grouping_key] = {
    #                 'tax_line': line,
    #                 'balance': 0.0,
    #                 'amount_currency': 0.0,
    #                 'tax_base_amount': 0.0,
    #                 'grouping_dict': False,
    #             }
    #     self.line_ids -= to_remove

    #     # ==== Mount base lines ====
    #     for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
    #         # Don't call compute_all if there is no tax.
    #         if not line.tax_ids:
    #             line.tag_ids = [(5, 0, 0)]
    #             continue

    #         compute_all_vals = _compute_base_line_taxes(line)

    #         # Assign tags on base line
    #         line.tag_ids = compute_all_vals['base_tags']

    #         tax_exigible = True
    #         for tax_vals in compute_all_vals['taxes']:
    #             grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
    #             grouping_key = _serialize_tax_grouping_key(grouping_dict)

    #             tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
    #             tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

    #             if tax.tax_exigibility == 'on_payment':
    #                 tax_exigible = False

    #             taxes_map_entry = taxes_map.setdefault(grouping_key, {
    #                 'tax_line': None,
    #                 'balance': 0.0,
    #                 'amount_currency': 0.0,
    #                 'tax_base_amount': 0.0,
    #                 'grouping_dict': False,
    #             })
    #             taxes_map_entry['balance'] += tax_vals['amount']
    #             taxes_map_entry['amount_currency'] += tax_vals.get('amount_currency', 0.0)
    #             taxes_map_entry['tax_base_amount'] += tax_vals['base']
    #             taxes_map_entry['grouping_dict'] = grouping_dict
    #         line.tax_exigible = tax_exigible

    #     # ==== Process taxes_map ====
    #     for taxes_map_entry in taxes_map.values():
    #         # Don't create tax lines with zero balance.
    #         if self.currency_id.is_zero(taxes_map_entry['balance']) and self.currency_id.is_zero(taxes_map_entry['amount_currency']):
    #             taxes_map_entry['grouping_dict'] = False

    #         tax_line = taxes_map_entry['tax_line']
    #         tax_base_amount = -taxes_map_entry['tax_base_amount'] if self.is_inbound() else taxes_map_entry['tax_base_amount']

    #         if not tax_line and not taxes_map_entry['grouping_dict']:
    #             continue
    #         elif tax_line and recompute_tax_base_amount:
    #             tax_line.tax_base_amount = tax_base_amount
    #         elif tax_line and not taxes_map_entry['grouping_dict']:
    #             # The tax line is no longer used, drop it.
    #             self.line_ids -= tax_line
    #         elif tax_line:
    #             tax_line.update({
    #                 'amount_currency': taxes_map_entry['amount_currency'],
    #                 'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
    #                 'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
    #                 'tax_base_amount': tax_base_amount,
    #             })
    #         else:
    #             create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
    #             tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
    #             tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
    #             tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
    #             tax_line = create_method({
    #                 'name': tax.name,
    #                 'move_id': self.id,
    #                 'partner_id': line.partner_id.id,
    #                 'company_id': line.company_id.id,
    #                 'company_currency_id': line.company_currency_id.id,
    #                 'quantity': 1.0,
    #                 'date_maturity': False,
    #                 'amount_currency': taxes_map_entry['amount_currency'],
    #                 'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
    #                 'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
    #                 'tax_base_amount': tax_base_amount,
    #                 'exclude_from_invoice_tab': True,
    #                 'tax_exigible': tax.tax_exigibility == 'on_invoice',
    #                 **taxes_map_entry['grouping_dict'],
    #             })

    #         if in_draft_mode:
    #             tax_line._onchange_amount_currency()
    #             tax_line._onchange_balance()
    # #endregion
    # #region _recompute_dynamic_lines
    # def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
    #     ''' Recompute all lines that depend of others.

    #     For example, tax lines depends of base lines (lines having tax_ids set). This is also the case of cash rounding
    #     lines that depend of base lines or tax lines depending the cash rounding strategy. When a payment term is set,
    #     this method will auto-balance the move with payment term lines.

    #     :param recompute_all_taxes: Force the computation of taxes. If set to False, the computation will be done
    #                                 or not depending of the field 'recompute_tax_line' in lines.
    #     '''
    #     for invoice in self:
    #         resolucion = self.env['l10n_co_factura.company_resolucion'].sudo().search([
    #             ('company_id', '=', invoice.company_id.id),
    #             ('journal_id', '=', invoice.journal_id.id),
    #             ('state', '=', 'active'),
    #         ], limit=1)
    #         # Dispatch lines and pre-compute some aggregated values like taxes.
    #         for line in invoice.line_ids:
    #             if line.recompute_tax_line:
    #                 recompute_all_taxes = True
    #                 line.recompute_tax_line = False

    #             if invoice.type == 'out_invoice' and resolucion.tipo == 'facturacion-electronica':
    #                 if line.price_unit==0:
    #                     recompute_all_taxes = True
    #                     line.recompute_tax_line = False


    #         # Compute taxes.
    #         if recompute_all_taxes:
    #             invoice._recompute_tax_lines()
    #         if recompute_tax_base_amount:
    #             invoice._recompute_tax_lines(recompute_tax_base_amount=True)

    #         if invoice.is_invoice(include_refacturapts=True):

    #             # Compute cash rounding.
    #             invoice._recompute_cash_rounding_lines()

    #             # Compute payment terms.
    #             invoice._recompute_payment_terms_lines()

    #             # Only synchronize one2many in onchange.
    #             if invoice != invoice._origin:
    #                 invoice.invoice_line_ids = invoice.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
    # #endregion
    # #region compute_discount
    # # Calculo de descuento sobre total de factura sin afectar base grabable
    # @api.onchange('amount_untaxed', 'invoice_discount', 'invoice_discount_percent', 'amount_untaxed',
    #               'enable_invoice_discount')
    # def compute_discount(self):
    #     for invoice in self:
    #         if invoice.amount_total:
    #             if invoice.invoice_discount_base:
    #                 if invoice.enable_invoice_discount == 'value' and invoice.amount_untaxed:
    #                     invoice.invoice_discount_percent = (invoice.invoice_discount * 100) / invoice.amount_untaxed
    #                 if invoice.enable_invoice_discount == 'percent' and invoice.amount_untaxed:
    #                     invoice.invoice_discount = (invoice.amount_untaxed * invoice.invoice_discount_percent) / 100
    #                 if not invoice.enable_invoice_discount:
    #                     invoice.invoice_discount = 0
    #                     invoice.invoice_discount_percent = 0
    #                     invoice.invoice_discount_text = ''
    #             else:
    #                 amount = invoice.amount_untaxed + invoice.amount_tax
    #                 if invoice.enable_invoice_discount == 'value' and invoice.amount_untaxed:
    #                     invoice.invoice_discount_percent = (invoice.invoice_discount * 100) / amount
    #                 if invoice.enable_invoice_discount == 'percent' and invoice.amount_untaxed:
    #                     invoice.invoice_discount = (amount * invoice.invoice_discount_percent) / 100
    #                 if not invoice.enable_invoice_discount:
    #                     invoice.invoice_discount = 0
    #                     invoice.invoice_discount_percent = 0
    #                     invoice.invoice_discount_text = ''

    #         invoice.amount_total = invoice.amount_untaxed + invoice.amount_tax - invoice.invoice_discount + invoice.invoice_charges_freight
    # # Fin Calculo descuento sobre total de factura
    # #endregion
    # #region compute_charges_freight
    # # Calculo del cargo sobre el total de factura sin afectar base gravable

    # @api.onchange('amount_untaxed', 'invoice_line_ids')
    # def compute_charges_freight(self):
    #     for invoice in self:
    #         if invoice.type in ['out_invoice', 'out_refund']:
    #             invoice.invoice_charges_freight = sum(line.price_subtotal for line in invoice.invoice_line_ids if line.product_id.enable_charges)
    #             invoice.amount_total = invoice.amount_untaxed + invoice.amount_tax - invoice.invoice_discount + invoice.invoice_charges_freight
    #             if invoice.amount_total:
    #                 invoice.invoice_charges_freight_percent = (invoice.invoice_charges_freight * 100) / invoice.amount_total

    # # Fin del calculo
    # #endregion
    # #region compute_fe_habilitada_compania
    # @api.depends('invoice_sequence_number_next')
    # def compute_fe_habilitada_compania(self):
    #     for record in self:
    #         if record.company_id:
    #             record.fe_habilitada_compania = record.company_id.fe_habilitar_facturacion
    #         else:
    #             record.fe_habilitada_compania = self.env.company.fe_habilitar_facturacion
    # #endregion
    # #region compute_company_partner_id
    # @api.depends('partner_id')
    # def compute_company_partner_id(self):
    #     for invoice in self:
    #         invoice.company_partner_id = self.env.company.partner_id
    # #endregion
    # #region compute_fe_habilitar_facturacion_related
    # @api.depends('company_id')
    # def compute_fe_habilitar_facturacion_related(self):
    #     for invoice in self:
    #         invoice.fe_habilitar_facturacion_related = self.company_id.fe_habilitar_facturacion
    # #endregion
    # #region line_discount_function crea l??nea en el create
    # #Actualizar!!!
    # def line_discount_function(self, values):
    #     line_ids_new = []
    #     line_invoice_ids_new = []
    #     line_discount_exist=False
    #     if not self:
    #         for line in values['line_ids']:
    #             if 'name' in line[2] and line[2]['name'] == 'Descuento A Total de Factura':
    #                 line_discount = True
    #                 line_discount_exist=True
    #             else:
    #                 line_ids_new.append(line)
    #                 line_discount = False
    #         if not line_discount_exist:
    #             if self.enable_invoice_discount or ('invoice_discount' in values and values['invoice_discount'] > 0) or (
    #                     'invoice_discount_percent' in values and values['invoice_discount_percent'] > 0):

    #                 if self.enable_invoice_discount:
    #                     if self.currency_id != self.company_id.currency_id:
    #                         discount_currency = self.currency_id._convert(self.invoice_discount, self.company_id.currency_id,
    #                                                                       self.company_id, self.date)
    #                         discount = self.invoice_discount
    #                     else:
    #                         discount = self.invoice_discount
    #                         discount_currency = 0
    #                 else:
    #                     company_id = self.env.companies
    #                     if 'enable_invoice_discount' in values and values['enable_invoice_discount']=='value':
    #                         if 'invoice_discount' in values and values['invoice_discount'] > 0:
    #                             if 'currency_id' in values and values['currency_id'] != company_id.currency_id.id:
    #                                 discount = values['invoice_discount']
    #                                 currency = company_id.env['res.currency'].sudo().search(
    #                                     [('id', '=', values['currency_id'])])
    #                                 discount_currency = currency._convert(discount, company_id.currency_id,
    #                                                                            company_id, values['date'])
    #                             else:
    #                                 discount = values['invoice_discount']
    #                                 discount_currency = 0
    #                     elif 'enable_invoice_discount' in values and values['enable_invoice_discount']=='percent':
    #                         if 'invoice_discount_base' in values and values['invoice_discount_base'] == True:
    #                             if 'currency_id' in values and values['currency_id'] != company_id.currency_id.id:
    #                                 amount = self.compute_amount_discount(values, True, True)
    #                                 discount_currency = (-amount * values['invoice_discount_percent']) / 100
    #                                 currency = company_id.env['res.currency'].sudo().search(
    #                                     [('id', '=', values['currency_id'])])
    #                                 discount = company_id.currency_id._convert(discount_currency, currency,
    #                                                                            company_id, values['date'])
    #                             else:
    #                                 amount = self.compute_amount_discount(values, True,False)
    #                                 discount = (-amount * values['invoice_discount_percent']) / 100
    #                                 discount_currency = 0
    #                         else:
    #                             if 'currency_id' in values and values['currency_id'] != company_id.currency_id.id:
    #                                 amount = self.compute_amount_discount(values, False, True)
    #                                 discount_currency = (-amount * values['invoice_discount_percent']) / 100
    #                                 currency = company_id.env['res.currency'].sudo().search(
    #                                     [('id', '=', values['currency_id'])])
    #                                 discount = company_id.currency_id._convert(discount_currency,currency,
    #                                                                       company_id, values['date'])

    #                             else:
    #                                 amount = self.compute_amount_discount(values, False,False)
    #                                 discount = (-amount * values['invoice_discount_percent']) / 100
    #                                 discount_currency=0
    #                         #discount = (-amount * values['invoice_discount_percent']) / 100
    #                         values['invoice_discount'] = abs(discount)

    #                     '''if 'currency_id' in values and values['currency_id'] != company_id.currency_id.id:
    #                         currency = company_id.env['res.currency'].search([('id', '=', values['currency_id'])])
    #                         discount_currency = currency._convert(discount, company_id.currency_id,
    #                                                               company_id, values['date'])
    #                     else:
    #                         discount_currency = 0'''


    #                 for line in values['line_ids']:
    #                     if line[2]['name'] == '' or line[2]['name'] == False:
    #                         if line[2]['price_unit'] < 0:
    #                             res = self.invoice_discount_get(False, abs(discount),values)
    #                             if not line_discount:
    #                                 line[2]['price_unit'] = line[2]['price_unit'] + abs(discount)
    #                                 if discount_currency != 0:
    #                                     if line[2]['debit'] > 0:
    #                                         line[2]['amount_currency'] = abs(line[2]['amount_currency'] - abs(discount))
    #                                     else:
    #                                         line[2]['amount_currency'] = line[2]['amount_currency'] + abs(discount)
    #                         else:
    #                             res = self.invoice_discount_get( True, abs(discount), values)
    #                             if not line_discount:
    #                                 line[2]['price_unit'] = line[2]['price_unit'] - abs(discount)
    #                                 if discount_currency != 0:
    #                                     if line[2]['debit'] > 0:
    #                                         line[2]['amount_currency'] = abs(line[2]['amount_currency'] - abs(discount))
    #                                     else:
    #                                         line[2]['amount_currency'] = line[2]['amount_currency'] + abs(discount)
    #                         if 'price_subtotal' in line[2]:
    #                             if line[2]['price_subtotal'] < 0:
    #                                 if not line_discount:
    #                                     line[2]['price_subtotal'] = line[2]['price_subtotal'] + abs(discount)
    #                             else:
    #                                 if not line_discount:
    #                                     line[2]['price_subtotal'] = line[2]['price_subtotal'] - abs(discount)
    #                         if 'price_total' in line[2]:
    #                             if line[2]['price_total'] < 0:
    #                                 if not line_discount:
    #                                     line[2]['price_total'] = line[2]['price_total'] + abs(discount)
    #                             else:
    #                                 if not line_discount:
    #                                     line[2]['price_total'] = line[2]['price_total'] - abs(discount)
    #                         if line[2]['debit'] > 0:
    #                             if discount_currency == 0:
    #                                 if not line_discount:
    #                                     line[2]['debit'] = line[2]['debit'] - abs(discount)
    #                             else:
    #                                 if not line_discount:
    #                                     line[2]['debit'] = line[2]['debit'] - abs(discount_currency)
    #                         else:
    #                             if discount_currency == 0:
    #                                 if not line_discount:
    #                                     line[2]['credit'] = line[2]['credit'] - abs(discount)
    #                             else:
    #                                 if not line_discount:
    #                                     line[2]['credit'] = line[2]['credit'] - abs(discount_currency)
    #                 line_ids_new.append((0, 0, res))
    #                 values['line_ids'] = line_ids_new
    #     else:
    #         value_change=False
    #         if ('invoice_discount_percent' in values or 'invoice_discount' in values):
    #             amount_invoice=self.amount_untaxed+self.amount_tax+self.invoice_charges_freight
    #             for line in self.line_ids:
    #                 if line.name == 'Descuento A Total de Factura':
    #                     line_discount = True
    #                 else:
    #                     line_ids_new.append(line)
    #                     line_discount = False
    #             for line in self.invoice_line_ids:
    #                 if line.name == 'Descuento A Total de Factura':
    #                     line_invoice_discount = True
    #                 else:
    #                     line_invoice_ids_new.append(line)
    #                     line_invoice_discount = False
    #             if self.enable_invoice_discount or (
    #                     'invoice_discount' in values and values['invoice_discount'] > 0) or (
    #                     'invoice_discount_percent' in values and values['invoice_discount_percent'] > 0):
    #                 company_id = self.env.companies
    #                 if 'invoice_discount' in values and values['invoice_discount'] > 0:
    #                     discount = values['invoice_discount']
    #                     if self.invoice_discount:
    #                         if self.invoice_discount!=discount:
    #                             value_change=True
    #                             self.invoice_discount = discount
    #                     else:
    #                         value_change = True
    #                         self.invoice_discount=discount
    #                 else:
    #                     value_change=False
    #                     if ('invoice_discount_base' in values and values['invoice_discount_base'] == True) or ('invoice_discount_base' not in values and self.invoice_discount_base):
    #                         amount = self.compute_amount_discount(values, True,False)
    #                     else:
    #                         amount = self.compute_amount_discount(values, False,False)
    #                     discount = (-amount * values['invoice_discount_percent']) / 100

    #                     if self.invoice_discount:
    #                         if self.invoice_discount!=discount:
    #                             value_change=True
    #                             values['invoice_discount'] = discount
    #                             self.invoice_discount = discount
    #                             self.invoice_discount = discount
    #                             self.invoice_discount_percent = values['invoice_discount_percent']
    #                     else:
    #                         value_change = True
    #                         values['invoice_discount'] = discount
    #                         self.invoice_discount=discount
    #                         self.invoice_discount = discount
    #                         self.invoice_discount_percent=values['invoice_discount_percent']

    #                 if value_change:
    #                     if 'currency_id' in values and values['currency_id'] != company_id.currency_id.id:
    #                         currency = company_id.env['res.currency'].sudo().search([('id', '=', values['currency_id'])])
    #                         discount_currency = currency._convert(discount, company_id.currency_id,
    #                                                               company_id, values['date'])
    #                     else:
    #                         discount_currency = 0
    #                     if 'date' in values:
    #                         date_invoice=values['date']
    #                     else:
    #                         date_invoice=self.date
    #                     if 'line_ids' in values:
    #                         for line in values['line_ids']:
    #                             if line[2]['name'] == '' or line[2]['name'] == False:
    #                                 if line[2]['price_unit'] < 0:
    #                                     res = self.invoice_discount_get( False, discount, values)
    #                                     if not line_discount:
    #                                         line[2]['price_unit'] = line[2]['price_unit'] + discount
    #                                         if discount_currency != 0:
    #                                             diferencia=amount_invoice-line[2]['amount_currency']
    #                                             line[2]['amount_currency'] = line[2]['amount_currency'] - discount +diferencia
    #                                 else:
    #                                     res = self.invoice_discount_get( True, discount, values)
    #                                     if not line_discount:
    #                                         line[2]['price_unit'] = line[2]['price_unit'] - discount
    #                                         if discount_currency != 0:
    #                                             diferencia = amount_invoice - line[2]['amount_currency']
    #                                             line[2]['amount_currency'] = line[2]['amount_currency'] + discount +diferencia
    #                                 if 'price_subtotal' in line[2]:
    #                                     if line[2]['price_subtotal'] < 0:
    #                                         if not line_discount:
    #                                             line[2]['price_subtotal'] = line[2]['price_subtotal'] + discount +diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             line[2]['price_subtotal'] = line[2]['price_subtotal'] - discount +diferencia
    #                                 if 'price_total' in line[2]:
    #                                     if line[2]['price_total'] < 0:
    #                                         if not line_discount:
    #                                             line[2]['price_total'] = line[2]['price_total'] + discount +diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             line[2]['price_total'] = line[2]['price_total'] - discount +diferencia
    #                                 if line[2]['debit'] > 0:
    #                                     if discount_currency == 0:
    #                                         if not line_discount:
    #                                             line[2]['debit'] = line[2]['debit'] - discount + diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             diferencia_currency= currency._convert(diferencia, company_id.currency_id,
    #                                                                   company_id, values['date'])
    #                                             line[2]['debit'] = line[2]['debit'] - discount_currency + diferencia_currency
    #                                 else:
    #                                     if discount_currency == 0:
    #                                         if not line_discount:
    #                                             line[2]['credit'] = line[2]['credit'] - discount + diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             line[2]['credit'] = line[2]['credit'] - discount_currency + diferencia_currency
    #                     else:
    #                         for line in self.line_ids:
    #                             if line.name == '' or line.name == False:
    #                                 if line.price_unit < 0:
    #                                     res = self.invoice_discount_get( False, discount, values)
    #                                     if not line_discount:
    #                                         line.price_unit = line.price_unit + discount
    #                                         if discount_currency != 0:
    #                                             diferencia=amount_invoice-line.amount_currency
    #                                             line.amount_currency = line.amount_currency - discount +diferencia
    #                                 else:
    #                                     res = self.invoice_discount_get( True, discount, values)
    #                                     if not line_discount:
    #                                         line.price_unit = line.price_unit - discount
    #                                         if discount_currency != 0:
    #                                             diferencia = amount_invoice - line.amount_currency
    #                                             line.amount_currency = line.amount_currency + discount +diferencia
    #                                 if line.price_subtotal:
    #                                     if line.price_subtotal < 0:
    #                                         if not line_discount:
    #                                             line.price_subtotal = line.price_subtotal + discount +diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             line.price_subtotal = line.price_subtotal - discount +diferencia
    #                                 if line.price_total:
    #                                     if line.price_total < 0:
    #                                         if not line_discount:
    #                                             line.price_total = line.price_total + discount +diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             line.price_total = line.price_total - discount +diferencia
    #                                 if line.debit > 0:
    #                                     if discount_currency == 0:
    #                                         if not line_discount:
    #                                             line.debit = line.debit - discount + diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             diferencia_currency= currency._convert(diferencia, company_id.currency_id,
    #                                                                   company_id, values['date'])
    #                                             line.debit = line.debit - discount_currency + diferencia_currency
    #                                 else:
    #                                     if discount_currency == 0:
    #                                         if not line_discount:
    #                                             line.credit = line.credit - discount + diferencia
    #                                     else:
    #                                         if not line_discount:
    #                                             line.credit = line.credit - discount_currency + diferencia_currency
    #                     line_ids_new.append((0, 0, res))
    #                     self.line_ids = line_ids_new
    #                     self.invoice_line_ids=line_invoice_ids_new

    #     return (self,values)
    # #endregion
    # #region _onchange_line_ids_discount
    # @api.onchange('invoice_line_ids')
    # def _onchange_line_ids_discount(self):
    #     if self.enable_invoice_discount:
    #         self.compute_discount()
    #         self._compute_amount()
    #         self._onchange_invoice_discount()
    #     else:
    #         self._compute_amount()
    # #endregion
    # #region _onchange_enable_invoice_discount
    # @api.onchange('enable_invoice_discount')
    # def _onchange_enable_invoice_discount(self):
    #     if self.enable_invoice_discount!='value' and self.enable_invoice_discount!='percent':
    #         move = self.env['account.move'].sudo().search([('id', '=', self.id.origin)])
    #         move.write({'invoice_discount': 0})
    #         move.write({'invoice_discount_percent': 0})
    #         self._onchange_invoice_discount()
    #     else:
    #         line_exist=False
    #         for line in self.line_ids:
    #             if line.name == 'Descuento A Total de Factura':
    #                 line_exist = True
    #         if not line_exist:
    #             if type(self.id)!=int:
    #                 if self.id.origin!=False:
    #                     move = self.env['account.move'].sudo().search([('id', '=', self.id.origin)])
    #                     val={}
    #                     move_dict=move.invoice_discount_get(False,0,val,True)
    #                     new_line=move.env['account.move.line'].create(move_dict)
    #                     self.line_ids+=new_line
    # #endregion
    # #region _onchange_invoice_discount_base
    # @api.onchange('invoice_discount_base')
    # def _onchange_invoice_discount_base(self):
    #     _logger.info('invoice_discount_base')
    #     self._onchange_invoice_discount()
    #     move = self.env['account.move'].sudo().search([('id', '=', self.id.origin)])
    #     move.invoice_discount_base=self.invoice_discount_base
    #     move.compute_discount()
    # #endregion

    # #region onchange invoice_discount
    # @api.onchange('invoice_discount','invoice_discount_percent','invoice_discount_view')
    # def _onchange_invoice_discount(self):
    #     self.compute_discount()
    #     taxes=self.env['account.tax'].sudo().search([('type_tax_use','=','sale')])
    #     impuestos=[]
    #     for tax in taxes:
    #         impuestos.append(tax.name)
    #     #_logger.info('Ingresa al onchange discount')
    #     for line in self.line_ids:
    #         if self.type == 'out_refund':
    #             if line.name == 'Descuento A Total de Factura':
    #                 if self.currency_id != self.company_id.currency_id:
    #                     discount_convert = self.currency_id._convert(self.invoice_discount,
    #                                                                   self.company_id.currency_id,
    #                                                                   self.company_id, self.date)
    #                     discount_currency = self.invoice_discount
    #                     value = discount_currency
    #                     value_convert=discount_convert
    #                     #_logger.info('Value')
    #                     #_logger.info(value)
    #                     line.update({
    #                         'price_unit': -value,
    #                         'price_subtotal': -value,
    #                         'price_total': -value,
    #                         'amount_currency': -value,
    #                         'credit': value_convert,
    #                         'debit': 0,
    #                         'balance': -value_convert,
    #                     })

    #                     amount = 0
    #                     amount_convert=0
    #                     for line in self.line_ids:
    #                         if line.debit != 0:
    #                             amount_convert += line.debit
    #                             amount += abs(line.price_subtotal)
    #                         if line.credit != 0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name in impuestos:
    #                                 amount_convert -=line.credit
    #                                 amount-=abs(line.price_subtotal)
    #                     for line in self.line_ids:
    #                         if line.credit != 0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name not in impuestos:
    #                                 #_logger.info('amount')
    #                                 #_logger.info(-amount - value)
    #                                 amount_update = amount - value
    #                                 amount_update_convert = amount_convert - value_convert

    #                                 line.update({
    #                                         'price_unit': -amount_update,
    #                                         'price_subtotal': -amount_update,
    #                                         'price_total': -amount_update,
    #                                         'amount_residual_currency': amount_update,
    #                                         'amount_currency': -amount_update,
    #                                         'credit': amount_update_convert,
    #                                         'debit': 0,
    #                                         'balance': -amount_update_convert,
    #                                         'amount_residual': amount_update_convert,
    #                                     })
    #                 else:
    #                     discount_currency = self.invoice_discount
    #                     value=discount_currency
    #                     #_logger.info('Value')
    #                     #_logger.info(value)
    #                     line.update({
    #                         'price_unit': value,
    #                         'price_subtotal': value,
    #                         'price_total': value,
    #                         'credit': -value,
    #                         'debit': 0,
    #                         'balance': value,
    #                     })
    #                     amount=0

    #                     for line in self.line_ids:
    #                         if line.debit!=0:
    #                             amount+=line.debit
    #                         if line.credit != 0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name in impuestos:
    #                                 amount -= line.credit
    #                     for line in self.line_ids:
    #                         if line.credit!=0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name not in impuestos:
    #                                 #_logger.info('amount')
    #                                 #_logger.info(-amount - value)
    #                                 amount_update = amount - value
    #                                 line.update({
    #                                     'price_unit': -amount_update,
    #                                     'price_subtotal': -amount_update,
    #                                     'price_total': -amount_update,
    #                                     'credit': amount_update,
    #                                     'debit': 0,
    #                                     'balance': -amount_update,
    #                                     'amount_residual': -amount_update,
    #                                 })

    #         elif self.type == 'out_invoice':
    #             if line.name == 'Descuento A Total de Factura':
    #                 if self.currency_id != self.company_id.currency_id:
    #                     discount_convert = self.currency_id._convert(self.invoice_discount,
    #                                                                  self.company_id.currency_id,
    #                                                                  self.company_id, self.date)
    #                     discount_currency = self.invoice_discount
    #                     value = discount_currency
    #                     value_convert = discount_convert
    #                     #_logger.info('value')
    #                     #_logger.info(value)
    #                     ##here
    #                     line.update({
    #                         'price_unit': -value,
    #                         'price_subtotal': -value,
    #                         'price_total': -value,
    #                         'amount_currency': value,
    #                         'debit': value_convert,
    #                         'credit': 0,
    #                         'balance': value_convert,
    #                     })
    #                     amount = 0
    #                     amount_convert=0
    #                     # descuento positivo
    #                     for line in self.line_ids:
    #                         if line.credit != 0:
    #                             amount_convert += line.credit
    #                             amount += abs(line.price_subtotal)
    #                         if line.debit != 0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name in impuestos:
    #                                 amount_convert -= line.debit
    #                                 amount -= abs(line.price_subtotal)
    #                     for line in self.line_ids:
    #                             if line.debit != 0 and line.name != 'Descuento A Total de Factura':
    #                                 if line.name not in impuestos:
    #                                     #_logger.info('amount')
    #                                     #_logger.info(-amount - value)
    #                                     amount_update = amount - value
    #                                     amount_update_convert = amount_convert - value_convert

    #                                     line.update({
    #                                         'price_unit': -amount_update,
    #                                         'price_subtotal': -amount_update,
    #                                         'price_total': -amount_update,
    #                                         'amount_residual_currency': amount_update,
    #                                         'amount_currency': amount_update,
    #                                         'debit': amount_update_convert,
    #                                         'credit': 0,
    #                                         'balance': amount_update_convert,
    #                                         'amount_residual': amount_update_convert,
    #                                     })
    #                 else:
    #                     discount_currency = self.invoice_discount
    #                     value = discount_currency
    #                     _logger.info('value')
    #                     _logger.info(value)
    #                     line.update({
    #                         'price_unit': -value,
    #                         'price_subtotal': -value,
    #                         'price_total': -value,
    #                         'debit': value,
    #                         'credit': 0,
    #                         'balance': value,
    #                     })
    #                     amount=0
    #                     #descuento positivo
    #                     for line in self.line_ids:
    #                         if line.credit!=0:
    #                             amount+=line.credit
    #                         if line.debit != 0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name in impuestos:
    #                                 amount -= line.debit
    #                     for line in self.line_ids:
    #                         if line.debit!=0 and line.name != 'Descuento A Total de Factura':
    #                             if line.name not in impuestos:
    #                                 _logger.info('amount')
    #                                 _logger.info(amount - value)
    #                                 amount_update = amount - value
    #                                 line.update({
    #                                     'price_unit': -amount_update,
    #                                     'price_subtotal': -amount_update,
    #                                     'price_total': -amount_update,
    #                                     'debit': amount_update,
    #                                     'credit': 0,
    #                                     'balance': amount_update,
    #                                     'amount_residual': amount_update,
    #                                 })
    #     if type(self.id) != int:
    #         if self.id.origin:
    #             move=self.env['account.move'].sudo().search([('id','=',self.id.origin)])
    #             move.line_ids=self.line_ids
    # #endregion

    # #region write
    # def write(self, values):
    #     for invoice in self:
    #         if invoice.es_factura_electronica == True and 'state' in values and values['state'] == 'cancel':
    #             raise ValidationError(u'No puede cancelar una factura electr??nica')
    #         elif invoice.es_factura_electronica == True and 'state' in values and 'enviada' not in values and values['state'] == 'draft':
    #             raise ValidationError(u'No puede Pasar a Borrador una factura electr??nica')
    #         else:
    #             if not invoice.invoice_discount_view and not invoice.invoice_charges_freight_view and (
    #                     invoice.amount_untaxed + invoice.amount_tax) != invoice.amount_total:
    #                 if 'cont' not in self.env.context and invoice.type in ['out_invoice', 'out_refund']:
    #                     ctx = self.env.context.copy()
    #                     ctx.update({
    #                         'cont': 1,
    #                     })
    #                     self.env.context = ctx
    #                     invoice.compute_discount()
    #                     invoice.compute_charges_freight()

    #             if invoice.type in ['out_invoice', 'out_refund']:
    #                 dato = ''
    #                 if 'state' in values and values['state'] == 'draft' and invoice.es_factura_electronica == True:
    #                     dato = 'Regeneracion de Factura'
    #                 elif 'state' in values and values['state'] == 'posted':
    #                     dato = 'Cambio de estado de Factura en Borrador a Abierta'
    #                 elif 'attachment_file' in values and values['attachment_file']:
    #                     dato = 'Cargo respuesta de la DIAN'
    #                 elif 'fe_approved' in values and values['fe_approved']=='sin-calificacion':
    #                     dato = 'carga de informacion base de aprobacion'
    #                 elif 'fe_approved' in values and values['fe_approved']=='aprobada':
    #                     dato = 'El cliente Aprobo la Factura'
    #                 elif 'fe_approved' in values and values['fe_approved']=='rechazada':
    #                     dato = 'El cliente Rechazo la Factura'
    #                 elif 'fe_approved' in values and values['fe_approved']=='aprobada_sistema':
    #                     dato = 'El sistema Aprobo la Factura'
    #                 writed = super(Invoice, self).write(values)

    #                 invoices = self.env['l10n_co_factura.history'].sudo().search([('factura', '=', invoice['id']), ('actividad', '=', 'Envio de Factura al Cliente')])
    #                 if dato != '' and writed:
    #                     val = {
    #                         'company_id': invoice['company_id'].id,
    #                         'actividad': dato,
    #                         'fecha_hora': invoice['write_date'],
    #                         'factura': invoice['id'],
    #                         'estado': invoice['state'],
    #                         'type': 'Factura Electronica' if invoice['type']=='out_invoice' and not invoice['es_nota_debito'] else 'Nota Debito' if invoice['type']=='out_invoice' and invoice['es_nota_debito'] else'Nota Credito',
    #                         'estado_validacion': invoice['fe_approved'],
    #                         'estado_dian': invoice.envio_fe_id.respuesta_validacion
    #                     }
    #                     if not invoices:
    #                         self.env['l10n_co_factura.history'].create(val)
    #                     if invoices and val['actividad'] in ['carga de informacion base de aprobacion','El cliente Aprobo la Factura','El cliente Rechazo la Factura','El sistema Aprobo la Factura']:
    #                         self.env['l10n_co_factura.history'].create(val)
    #                     else:
    #                         _logger.info('estado de actividad existente')
    #             else:
    #                 writed = super(Invoice, self).write(values)

    #             return writed
    # #endregion

    # #region create
    # @api.model
    # def create(self, values):
    #     rate_exchange_module = self.env['ir.module.module'].sudo().search([('name', '=', 'manual_rate_exchange')])
    #     if len(rate_exchange_module) > 0:
    #         if rate_exchange_module.state == 'installed':
    #             self.validate_check_rate(values)
    #     if 'line_ids' in values:
    #         self,values=self.line_discount_function(values)
    #     if 'currency_id' in values:
    #         if 'company_id' in values:
    #             company=values['company_id']
    #             user=self.env.user
    #             company_id=self.env['res.company'].sudo().search([('id','=',company)])
    #         else:
    #             company_id = self.env.companies
    #         currency = company_id.env['res.currency'].sudo().search([('id', '=', values['currency_id'])])
    #         if currency.id != company_id.currency_id.id:
    #             if 'type' in values and (values['type']=='out_invoice' or values['type']=='out_refund'):
    #                 values['es_factura_exportacion']=True

    #     created = super(Invoice, self).create(values)
    #     if created.type in ['out_invoice','out_refund']:
    #         created.compute_discount()
    #         created.compute_charges_freight()
    #         #created._compute_amount()
    #         val = {
    #             'company_id': created['company_id'].id,
    #             'actividad': 'Recepci??n y creaci??n de Factura',
    #             'fecha_hora': created['create_date'],
    #             'factura': created['id'],
    #             'estado': created['state'],
    #             'type': 'Factura Electronica' if created['type']=='out_invoice' and not created['es_nota_debito'] else 'Nota Debito' if created['type']=='out_invoice' and created['es_nota_debito'] else'Nota Credito',
    #             'estado_validacion': created['fe_approved']
    #         }
    #         self.env['l10n_co_factura.history'].create(val)
    #         if created.type == 'out_invoice' and created.es_nota_debito:
    #             created.ref = 'Nota debito:' + created.invoice_partner_display_name
    #         if created.fe_habilitar_facturacion_related:
    #             created.es_factura_electronica = True
    #     return created
    # #endregion

    # #region get_current_invoice_currency
    # def get_current_invoice_currency(self):
    #     other_currency = False
    #     if self.company_id.currency_id.id != self.currency_id.id:
    #         other_currency = True

    #     return other_currency
    # #endregion

    # #region action_generar_nota_debito
    # def action_generar_nota_debito(self):
    #     # self.es_nota_debito = True

    #     invoice_form = self.env.ref('l10n_co_factura.l10n_co_factura_invoice_form', False)
    #     journal = self.env['account.journal'].sudo().search([('categoria', '=', 'nota-debito')], limit=1)

    #     for invoice in self:
    #         ctx = dict(
    #             default_partner_id=invoice.partner_id.id,
    #             default_es_nota_debito=True,
    #             default_credited_invoice_id=invoice.id,
    #             default_journal_id=journal.id,
    #             default_type='out_invoice',
    #         )
    #         if invoice.get_current_invoice_currency():
    #             ctx['default_currency_id'] = invoice.currency_id.id

    #     return {
    #         'name': 'Agregar nota d??bito',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'account.move',
    #         'views': [(invoice_form.id, 'form')],
    #         'view_id': invoice_form.id,
    #         'target': 'new',
    #         'context': ctx
    #     }
    # #endregion
    # #region action_regenerar_xml
    # def action_regenerar_xml(self):
    #     # Permite regenerar XML de la factura en caso de respuesta fallida
    #     # al validar con la DIAN

    #     for invoice in self:
    #         if not self.envio_fe_id or (self.envio_fe_id and self.envio_fe_id.codigo_respuesta_validacion != '00'):

    #             envio = invoice.env['l10n_co_factura.envio_fe'].sudo().search([('id', '=', invoice.envio_fe_id.id)], limit=1)
    #             envio.unlink()

    #             moves = self.env['account.move']
    #             for inv in self:
    #                 inv.line_ids.filtered(lambda x: x.account_id.reconcile).remove_move_reconcile()

    #             # First, set the invoices as cancelled and detach the move ids
    #             invoice.write({'state': 'draft', 'enviada': False})
    #             validate = self.env['ir.model.fields'].search([('name', '=', 'is_anglo_saxon_line'), ('model', '=', 'account.move.line')])
    #             if validate:
    #                 lines = self.with_context(check_move_validity=False).env['account.move.line'].sudo().search([('move_id', '=', invoice.id)])
    #                 for line in lines:
    #                     if line['is_anglo_saxon_line']:
    #                         line.with_context({'check_move_validity': False}).unlink()
    #                     analytic_lines = self.env['account.analytic.line'].search([('move_id', '=', line.id)])
    #                     for analytic_line in analytic_lines:
    #                         analytic_line.with_context({'check_move_validity': False}).unlink()

    #             if moves:
    #                 # second, invalidate the move(s)
    #                 moves.button_draft()
    #                 # delete the move this invoice was pointing to
    #                 # Note that the corresponding move_lines and move_reconciles
    #                 # will be automatically deleted too
    #                 moves.unlink()

    #             invoice.write({
    #                 'filename': None,
    #                 'firmado': False,
    #                 'file': None,
    #                 'zipped_file': None,
    #                 'nonce': None,
    #                 'qr_code': None,
    #                 'cufe': None,
    #                 'enviada': False,
    #                 'enviada_error': False,
    #                 'envio_fe_id': None,
    #                 'attachment_id': None,
    #                 'state': 'draft',
    #             })

    #             if invoice.type == 'out_invoice':
    #                 _logger.info('Factura {} regenerada correctamente'.format(invoice.name))
    #             elif invoice.type == 'out_refund':
    #                 _logger.info('Nota cr??dito {} regenerada correctamente'.format(invoice.name))
    #         else:
    #             _logger.error('No es posible regenerar el documento {}'.format(invoice.name))
    #             raise ValidationError('No es posible regenerar el documento {}'.format(invoice.name))
    # #endregion
    # #region compute_fe_tercero_to_email
    # def compute_fe_tercero_to_email(self):
    #     for invoice in self:
    #         config_fe = invoice._get_config()
    #         if invoice.es_factura_electronica and invoice.fe_habilitar_facturacion_related and invoice.type not in ['in_invoice', 'in_refund'] and invoice.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             return config_fe.get_value(
    #                 field_name=ConfigFE.tercero_to_email.name,
    #                 obj_id=invoice.id
    #             )
    #         else:
    #             return None
    # #endregion
    # #region compute_fe_company_email_from
    # @api.depends('partner_id')
    # def compute_fe_company_email_from(self):
    #     for invoice in self:
    #         config_fe = invoice._get_config()
    #         if invoice.es_factura_electronica and invoice.fe_habilitar_facturacion_related and invoice.type not in ['in_invoice', 'in_refund'] and invoice.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             invoice.fe_company_email_from = str(config_fe.get_value(
    #                 field_name=ConfigFE.company_email_from.name,
    #                 obj_id=invoice.id
    #             ))
    #         else:
    #             invoice.fe_company_email_from = None
    # #endregion
    # #region  _amount_int_text
    # def _amount_int_text(self):
    #     for rec in self:
    #         dec, cent = amount_to_text_es("{0:.2f}".format(rec.amount_total))
    #         rec.amount_total_text = dec
    #         rec.amount_total_text_cent = cent

    # # endregion
    # # region _get_config
    # def _get_config(self):
    #     return self.env['l10n_co_factura.config_fe'].sudo().search(
    #         [],
    #         limit=1
    #     )

    # # endregion
    # # region _unload_config_data
    # def _unload_config_data(self):
    #     # global fe_company
    #     # global fe_tercero
    #     # global fe_sucursal_data
    #     self.fe_company = None
    #     self.fe_tercero = None
    #     self.parent_fe_tercero = None
    #     self.fe_sucursal_data = None

    # # endregion
    # # region _load_config_data

    # def _load_config_data(self):
    #     for invoice in self:
    #         config_fe = invoice._get_config()
    #         # config set up
    #         # global fe_company
    #         # global fe_tercero
    #         # global fe_sucursal_data

    #         if invoice.es_factura_electronica and invoice.fe_habilitar_facturacion_related and invoice.type not in ['in_invoice', 'in_refund'] and invoice.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             self.fe_company = {
    #                 ConfigFE.company_tipo_documento.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_tipo_documento.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_nit.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_nit.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_direccion.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_direccion.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_postal.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_postal.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_pais.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_pais.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_departamento.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_departamento.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_ciudad.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_ciudad.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_tipo_regimen.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_tipo_regimen.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_digito_verificacion.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_digito_verificacion.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_telefono.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_telefono.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_email_from.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_email_from.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_matricula_mercantil.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_matricula_mercantil.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_responsabilidad_fiscal.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_responsabilidad_fiscal.name,
    #                     obj_id=invoice.id
    #                 ),
    #                 ConfigFE.company_responsabilidad_tributaria.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_responsabilidad_tributaria.name,
    #                     obj_id=invoice.id
    #                 ),
    #             }
    #             if self.partner_id.fe_facturador:
    #                 self.fe_tercero = {
    #                     ConfigFE.tercero_es_compania.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_es_compania.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_postal.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_postal.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_pais.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_pais.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_ciudad.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_ciudad.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_departamento.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_departamento.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_direccion.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_direccion.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_razon_social.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_razon_social.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.tercero_primer_apellido.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_primer_apellido.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.tercero_segundo_apellido.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_segundo_apellido.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.tercero_primer_nombre.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_primer_nombre.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.tercero_segundo_nombre.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_segundo_nombre.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.tercero_nit.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_nit.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_tipo_documento.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_tipo_documento.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_tipo_regimen.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_tipo_regimen.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_digito_verificacion.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_digito_verificacion.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_telefono.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_telefono.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_to_email.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_to_email.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_matricula_mercantil.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_matricula_mercantil.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_responsabilidad_fiscal.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_responsabilidad_fiscal.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.tercero_responsabilidad_tributaria.name: config_fe.get_value(
    #                         field_name=ConfigFE.tercero_responsabilidad_tributaria.name,
    #                         obj_id=invoice.id
    #                     ),
    #                 }
    #             if self.partner_id.parent_id and not self.partner_id.fe_facturador:
    #                 self.parent_fe_tercero = {
    #                     ConfigFE.padre_tercero_es_compania.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_es_compania.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_postal.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_postal.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_pais.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_pais.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_ciudad.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_ciudad.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_departamento.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_departamento.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_direccion.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_direccion.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_razon_social.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_razon_social.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.padre_tercero_primer_apellido.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_primer_apellido.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.padre_tercero_segundo_apellido.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_segundo_apellido.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.padre_tercero_primer_nombre.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_primer_nombre.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.padre_tercero_segundo_nombre.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_segundo_nombre.name,
    #                         obj_id=invoice.id,
    #                         can_be_null=True
    #                     ),
    #                     ConfigFE.padre_tercero_nit.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_nit.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_tipo_documento.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_tipo_documento.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_tipo_regimen.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_tipo_regimen.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_digito_verificacion.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_digito_verificacion.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_telefono.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_telefono.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_to_email.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_to_email.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_matricula_mercantil.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_matricula_mercantil.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_responsabilidad_fiscal.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_responsabilidad_fiscal.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.padre_tercero_responsabilidad_tributaria.name: config_fe.get_value(
    #                         field_name=ConfigFE.padre_tercero_responsabilidad_tributaria.name,
    #                         obj_id=invoice.id
    #                     ),
    #                 }
    #             if self.fe_sucursal:
    #                 self.fe_sucursal_data = {
    #                     ConfigFE.sucursal_postal.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_postal.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.sucursal_pais.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_pais.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.sucursal_ciudad.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_ciudad.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.sucursal_departamento.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_departamento.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.sucursal_direccion.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_direccion.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.sucursal_telefono.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_telefono.name,
    #                         obj_id=invoice.id
    #                     ),
    #                     ConfigFE.sucursal_to_email.name: config_fe.get_value(
    #                         field_name=ConfigFE.sucursal_to_email.name,
    #                         obj_id=invoice.id
    #                     ),
    #                 }
    #     return self.fe_company, self.fe_tercero, self.fe_sucursal_data, self.parent_fe_tercero

    # # endregion
    # # region compute_fe_company_nit
    # def compute_fe_company_nit(self):
    #     for invoice in self:
    #         config_fe = invoice._get_config()
    #         if invoice.es_factura_electronica and invoice.fe_habilitar_facturacion_related and invoice.type not in ['in_invoice', 'in_refund'] and invoice.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             return config_fe.get_value(
    #                 field_name=ConfigFE.company_nit.name,
    #                 obj_id=invoice.id
    #             )
    #         else:
    #             return None

    # # endregion
    # # region compute_fe_company_digito_verificacion

    # def compute_fe_company_digito_verificacion(self):
    #     for invoice in self:
    #         config_fe = invoice._get_config()
    #         if invoice.es_factura_electronica and invoice.fe_habilitar_facturacion_related and invoice.type not in ['in_invoice', 'in_refund'] and invoice.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             return config_fe.get_value(
    #                 field_name=ConfigFE.company_digito_verificacion.name,
    #                 obj_id=invoice.id
    #             )
    #         else:
    #             return None

    # # endregion
    # # region compute_fe_tercero_nit

    # def compute_fe_tercero_nit(self):
    #     for invoice in self:
    #         config_fe = invoice._get_config()
    #         if invoice.es_factura_electronica and invoice.fe_habilitar_facturacion_related and invoice.type not in ['in_invoice', 'in_refund'] and invoice.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             return config_fe.get_value(
    #                 field_name=ConfigFE.tercero_nit.name,
    #                 obj_id=invoice.id
    #             )
    #         else:
    #             return None

    # # endregion
    # # region _get_fe_filename
    # def _get_fe_filename(self):
    #     try:
    #         for invoice in self:
    #             if invoice.filename:
    #                 return invoice.filename
    #             nit = str(self.fe_company[ConfigFE.company_nit.name]).zfill(10)
    #             current_year = datetime.datetime.now().replace(tzinfo=pytz.timezone('America/Bogota')).strftime('%Y')


    #     except Exception as e:
    #         _logger.error('[!] por favor valide el numero de documento y tipo de documento del cliente y la compa??ia en el modulo de contactos para la factura {} - Excepci??n: {}'.format(self.invoice_payment_ref, e))
    #         raise ValidationError('[!] por favor valide el numero de documento y tipo de documento del cliente y la compa??ia en el modulo de contactos para la factura {} - Excepci??n: {}'.format(self.invoice_payment_ref, e))

    #     try:
    #         # TODO: Migrar a Odoo 9, 10 y 11
    #         # Multicompa????a habilitado de forma experimental
    #         if invoice.type == 'out_invoice' and not invoice.es_nota_debito:
    #             # sequence = self.env.ref('l10n_co_factura.dian_invoice_sequence', False)
    #             sequence = self.env['ir.sequence'].sudo().search([
    #                 ('company_id', '=', invoice.company_id.id), ('fe_tipo_secuencia', '=', 'facturas-venta')], limit=1)
    #         elif invoice.type == 'out_refund':
    #             # sequence = self.env.ref('l10n_co_factura.dian_credit_note_sequence', False)
    #             sequence = self.env['ir.sequence'].sudo().search([
    #                 ('company_id', '=', invoice.company_id.id), ('fe_tipo_secuencia', '=', 'notas-credito')], limit=1)
    #         else:
    #             # sequence = self.env.ref('l10n_co_factura.dian_debit_note_sequence', False)
    #             sequence = self.env['ir.sequence'].sudo().search([
    #                 ('company_id', '=', invoice.company_id.id), ('fe_tipo_secuencia', '=', 'notas-debito')], limit=1)

    #         if invoice.type == 'out_invoice' and not invoice.es_nota_debito:
    #             if invoice.name:
    #                 filename = 'fv{}000{}{}'.format(nit, current_year[-2:], str(invoice.name).replace(sequence.prefix,'').zfill(8))
    #             else:
    #                 filename = 'fv{}000{}{}'.format(nit, current_year[-2:], str(sequence.number_next_actual).zfill(8))
    #         elif invoice.type == 'out_refund':
    #             if invoice.name:
    #                 filename = 'nc{}000{}{}'.format(nit, current_year[-2:], str(invoice.name).replace(sequence.prefix,'').zfill(8))
    #             else:
    #                 filename = 'nc{}000{}{}'.format(nit, current_year[-2:], str(sequence.number_next_actual).zfill(8))
    #         else:
    #             if invoice.name:
    #                 filename = 'nd{}000{}{}'.format(nit, current_year[-2:], str(invoice.name).replace(sequence.prefix,'').zfill(8))
    #             else:
    #                 filename = 'nd{}000{}{}'.format(nit, current_year[-2:], str(sequence.number_next_actual).zfill(8))

    #         return filename

    #     except Exception as e:
    #         _logger.error('[!] por favor valide las configuraciones de la secuencia, diario y resolucion para el documento {} - Excepci??n: {}'.format(self.invoice_payment_ref, e))
    #         raise ValidationError('[!] por favor valide las configuraciones de la secuencia, diario y resolucion para el documento {} - Excepci??n: {}'.format(self.invoice_payment_ref, e))

    # # endregion
    # # region generar_factura_electronica
    # # genera xml de facturacion electronica

    # def generar_factura_electronica(self):
    #     if len(self) != 1:
    #         raise ValidationError(
    #             "Esta opci??n solo debe ser usada por ID individual a la vez."
    #         )
    #     for invoice in self:
    #         if (invoice.type == 'out_invoice' and
    #                 not invoice.company_resolucion_id.tipo == 'facturacion-electronica'):
    #             raise ValidationError(
    #                 "Esta funci??n es solo para facturaci??n electr??nica."
    #             )
    #         if invoice.file:
    #             raise ValidationError(
    #                 "La factura electr??nica ya fue generada."
    #             )

    #         if invoice.type == 'out_invoice' and not invoice.company_resolucion_id:
    #             raise ValidationError(
    #                 "La factura no est?? vinculada a una resoluci??n."
    #             )
    #         if not invoice.file:
    #             output = ''
    #             if invoice.type == 'out_invoice':
    #                 if invoice.es_nota_debito:
    #                     output = invoice.generar_creditnote_xml()
    #                     _logger.info('Nota d??bito {} generada'.format(invoice.name))
    #                 else:
    #                     output = invoice.generar_invoice_xml()
    #                     _logger.info('Factura {} generada'.format(invoice.name))
    #             elif invoice.type == 'out_refund':
    #                 output = invoice.generar_creditnote_xml()
    #                 _logger.info('Nota cr??dito {} generada'.format(invoice.name))

    #             invoice.sudo().write({
    #                 'file': base64.b64encode(output.encode())
    #             })

    # # endregion
    # # region prefix_invoice_number
    # def prefix_invoice_number(self):
    #     for invoice in self:
    #         if invoice.type == 'out_invoice':
    #             if invoice.company_resolucion_id.journal_id.sequence_id:
    #                 return invoice.name
    #             else:
    #                 prefijo = invoice.company_resolucion_id.prefijo
    #             return (prefijo if prefijo else '') + invoice.name
    #         else:  # Necesario para evitar errores cuando se le asigna prefijo a secuencia de nota c??edito.
    #             if invoice.company_resolucion_id.journal_id.refund_sequence_id:
    #                 return invoice.name
    #             else:
    #                 prefijo = invoice.company_resolucion_id.prefijo_nota
    #                 return (prefijo if prefijo else '') + invoice.name

    # # endregion
    # # region _tipo_de_documento
    # def _tipo_de_documento(self, tipo_de_documento):
    #     return str(tipo_de_documento)

    # # endregion
    # # region _str_to_datetime
    # @staticmethod
    # def _str_to_datetime(date):
    #     date = date.replace(tzinfo=pytz.timezone('UTC'))
    #     return date

    # # endregion
    # # region calcular_cufe
    # def calcular_cufe(self, tax_total_values):

    #     create_date = self._str_to_datetime(self.fecha_xml)
    #     tax_computed_values = {tax: value['total'] for tax, value in tax_total_values.items()}

    #     numfac = self.prefix_invoice_number()
    #     fecfac = create_date.astimezone(pytz.timezone('America/Bogota')).strftime('%Y-%m-%d')
    #     horfac = create_date.astimezone(pytz.timezone('America/Bogota')).strftime('%H:%M:%S-05:00')
    #     valfac = '{:.2f}'.format(self.amount_untaxed)
    #     codimp1 = '01'
    #     valimp1 = '{:.2f}'.format(tax_computed_values.get('01', 0))
    #     codimp2 = '04'
    #     valimp2 = '{:.2f}'.format(tax_computed_values.get('04', 0))
    #     codimp3 = '03'
    #     valimp3 = '{:.2f}'.format(tax_computed_values.get('03', 0))
    #     valtot = '{:.2f}'.format(self.amount_total+self.total_withholding_amount) #if self.currency_id.name=='COP' else '{:.2f}'.format(self.amount_residual+self.total_withholding_amount-self.invoice_discount+self.invoice_charges_freight)
    #     nitofe = self.fe_company[ConfigFE.company_nit.name]
    #     if self.company_id.fe_tipo_ambiente != '3':
    #         tipoambiente = self.company_id.fe_tipo_ambiente
    #     else:
    #         tipoambiente = '2'
    #     if self.partner_id.fe_facturador:
    #         numadq = self.fe_tercero[ConfigFE.tercero_nit.name]
    #     else:
    #         numadq = self.parent_fe_tercero[ConfigFE.padre_tercero_nit.name]

    #     if self.type == 'out_invoice' and not self.es_nota_debito:
    #         citec = self.company_resolucion_id.clave_tecnica
    #     else:
    #         citec = self.company_id.fe_software_pin

    #     total_otros_impuestos = sum([value for key, value in tax_computed_values.items() if key != '01'])
    #     iva = tax_computed_values.get('01', '0.00')

    #     cufe = (
    #             numfac + fecfac + horfac + valfac + codimp1 + valimp1 + codimp2 +
    #             valimp2 + codimp3 + valimp3 + valtot + nitofe + numadq + citec +
    #             tipoambiente
    #     )
    #     cufe_seed = cufe
    #     #print('cufe:',cufe)
    #     #raise ValidationError("Detenido para revisar CUFE")
    #     sha384 = hashlib.sha384()
    #     sha384.update(cufe.encode())
    #     cufe = sha384.hexdigest()

    #     qr_code = 'NumFac: {}\n' \
    #               'FecFac: {}\n' \
    #               'HorFac: {}\n' \
    #               'NitFac: {}\n' \
    #               'DocAdq: {}\n' \
    #               'ValFac: {}\n' \
    #               'ValIva: {}\n' \
    #               'ValOtroIm: {:.2f}\n' \
    #               'ValFacIm: {}\n' \
    #               'CUFE: {}'.format(
    #                 numfac,
    #                 fecfac,
    #                 horfac,
    #                 nitofe,
    #                 numadq,
    #                 valfac,
    #                 iva,
    #                 total_otros_impuestos,
    #                 valtot,
    #                 cufe
    #                 )

    #     qr = pyqrcode.create(qr_code, error='L')

    #     self.write({
    #         'cufe_seed': cufe_seed,
    #         'cufe': cufe,
    #         'qr_code': qr.png_as_base64_str(scale=2)
    #     })

    #     return self.cufe

    # # endregion
    # # region get_template_str
    # def get_template_str(self, relative_file_path):
    #     template_file = os.path.realpath(
    #         os.path.join(
    #             os.getcwd(),
    #             os.path.dirname(__file__),
    #             relative_file_path
    #         )
    #     )

    #     f = open(template_file, 'rU')
    #     # xml_template = f.read().decode('utf-8')
    #     xml_template = f.read()
    #     f.close()

    #     return xml_template

    # # endregion
    # # region generar_invoice_xml
    # def generar_invoice_xml(self):
    #     try:
    #         self.fe_company, self.fe_tercero, self.fe_sucursal_data, self.parent_fe_tercero = self._load_config_data()
    #         invoice = self
    #         self.fecha_xml = datetime.datetime.combine(self.invoice_date, datetime.datetime.now().time())
    #         create_date = self._str_to_datetime(self.fecha_xml)
    #         deliver_date = self._str_to_datetime(self.fecha_entrega)

    #         key_data = '{}{}{}'.format(
    #             invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin, invoice.prefix_invoice_number()
    #         )
    #         sha384 = hashlib.sha384()
    #         sha384.update(key_data.encode())
    #         software_security_code = sha384.hexdigest()

    #         reconciled_vals=self._get_reconciled_info_JSON_values()
    #         invoice_prepaids = []
    #         for reconciled_val in reconciled_vals:
    #             move_line_pago = self.env['account.move.line'].sudo().search([('id','=',reconciled_val.get('payment_id'))])
    #             mapa_prepaid={
    #                 'id': reconciled_val.get('payment_id'),
    #                 'paid_amount': reconciled_val.get('amount'),
    #                 'currency_id': str(self.currency_id.name),
    #                 'refacturaved_date': str(move_line_pago.date),
    #                 'paid_date': str(move_line_pago.date),
    #                 'paid_time': '12:00:00'
    #             }
    #             invoice_prepaids.append(mapa_prepaid)

    #         invoice_lines = []
    #         tax_exclusive_amount = 0
    #         #tax_values=[]
    #         self.total_withholding_amount = 0.0
    #         tax_total_values = {}
    #         ret_total_values = {}

    #         # Bloque de c??digo para imitar la estructura requerida por el XML de la DIAN para los totales externos
    #         # a las l??neas de la factura.
    #         for line_id in self.invoice_line_ids:
    #             for tax in line_id.tax_ids:
    #                 if '-' not in str(tax.amount):
    #                     # Inicializa contador a cero para cada ID de impuesto
    #                     if tax.codigo_fe_dian not in tax_total_values:
    #                         tax_total_values[tax.codigo_fe_dian] = dict()
    #                         tax_total_values[tax.codigo_fe_dian]['total'] = 0
    #                         tax_total_values[tax.codigo_fe_dian]['info'] = dict()

    #                     # Suma al total de cada c??digo, y a??ade informaci??n por cada tarifa.
    #                     if line_id.price_subtotal != 0:
    #                                 price_subtotal_calc = line_id.price_subtotal
    #                     else:
    #                         taxes = False
    #                         if line_id.tax_line_id:
    #                             taxes = line_id.tax_line_id.compute_all(line_id.line_price_reference, line_id.currency_id, line_id.quantity,product=line_id.product_id,partner=self.partner_id)
    #                         price_subtotal_calc = taxes['total_excluded'] if taxes else line_id.quantity * line_id.line_price_reference
                        
    #                     if tax.amount not in tax_total_values[tax.codigo_fe_dian]['info']:

    #                         aux_total = tax_total_values[tax.codigo_fe_dian]['total']
    #                         aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                         aux_total = round(aux_total, 2)
    #                         tax_total_values[tax.codigo_fe_dian]['total'] = aux_total
    #                         tax_total_values[tax.codigo_fe_dian]['info'][tax.amount] = {
    #                             'taxable_amount': price_subtotal_calc,
    #                             'value': round(price_subtotal_calc * tax['amount'] / 100, 2),
    #                             'technical_name': tax.tipo_impuesto_id.name,
    #                         }
                            
    #                     else:
                            
    #                         aux_tax = tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['value']
    #                         aux_total = tax_total_values[tax.codigo_fe_dian]['total']
    #                         aux_taxable = tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount']
    #                         aux_tax = aux_tax + price_subtotal_calc * tax['amount'] / 100
    #                         aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                         aux_taxable = aux_taxable + price_subtotal_calc
    #                         aux_tax = round(aux_tax, 2)
    #                         aux_total = round(aux_total, 2)
    #                         aux_taxable = round(aux_taxable, 2)
    #                         tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['value'] = aux_tax
    #                         tax_total_values[tax.codigo_fe_dian]['total'] = aux_total
    #                         tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount'] = aux_taxable
                            
    #                 else:
    #                     # Inicializa contador a cero para cada ID de impuesto
    #                     if tax.codigo_fe_dian not in ret_total_values:
    #                         ret_total_values[tax.codigo_fe_dian] = dict()
    #                         ret_total_values[tax.codigo_fe_dian]['total'] = 0
    #                         ret_total_values[tax.codigo_fe_dian]['info'] = dict()

    #                     # Suma al total de cada c??digo, y a??ade informaci??n por cada tarifa.
    #                     if line_id.price_subtotal != 0:
    #                         price_subtotal_calc = line_id.price_subtotal
    #                     else:
    #                         taxes = False
    #                         if line_id.tax_line_id:
    #                             taxes = line_id.tax_line_id.compute_all(line_id.line_price_reference, line_id.currency_id, line_id.quantity,product=line_id.product_id,partner=self.partner_id)
    #                         price_subtotal_calc = taxes['total_excluded'] if taxes else line_id.quantity * line_id.line_price_reference
    #                     if abs(tax.amount) not in ret_total_values[tax.codigo_fe_dian]['info']:

                            
    #                         aux_total = ret_total_values[tax.codigo_fe_dian]['total']
    #                         aux_total = aux_total + price_subtotal_calc * abs(tax['amount']) / 100
    #                         aux_total = round(aux_total, 2)
    #                         ret_total_values[tax.codigo_fe_dian]['total'] = abs(aux_total)

    #                         ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)] = {
    #                             'taxable_amount': abs(price_subtotal_calc),
    #                             'value': abs(round(price_subtotal_calc* tax['amount'] / 100, 2)),
    #                             'technical_name': tax.tipo_impuesto_id.name,
    #                         }
                          
    #                     else:
    #                         aux_tax = ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['value']
    #                         aux_total = ret_total_values[tax.codigo_fe_dian]['total']
    #                         aux_taxable = ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['taxable_amount']
    #                         aux_tax = aux_tax + price_subtotal_calc * abs(tax['amount']) / 100
    #                         aux_total = aux_total + price_subtotal_calc * abs(tax['amount']) / 100
    #                         aux_taxable = aux_taxable + price_subtotal_calc
    #                         aux_tax = round(aux_tax, 2)
    #                         aux_total = round(aux_total, 2)
    #                         aux_taxable = round(aux_taxable, 2)
    #                         ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['value'] = abs(aux_tax)
    #                         ret_total_values[tax.codigo_fe_dian]['total'] = abs(aux_total)
    #                         ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['taxable_amount'] = abs(aux_taxable)
                            
    #         for ret in ret_total_values.items():
    #             self.total_withholding_amount += abs(ret[1]['total'])

    #         contador = 1
    #         total_impuestos = 0
    #         for index, invoice_line_id in enumerate(self.invoice_line_ids):
    #             if not invoice_line_id.product_id.enable_charges and invoice_line_id.price_unit>=0:
    #                 if invoice_line_id.price_subtotal != 0:
    #                     price_subtotal_calc = invoice_line_id.price_subtotal
    #                 else:
    #                     taxes = False
    #                     if invoice_line_id.tax_line_id:
    #                         taxes = invoice_line_id.tax_line_id.compute_all(invoice_line_id.line_price_reference, invoice_line_id.currency_id, invoice_line_id.quantity,product=invoice_line_id.product_id,partner=self.partner_id)
    #                     price_subtotal_calc = taxes['total_excluded'] if taxes else invoice_line_id.quantity * invoice_line_id.line_price_reference
                    
    #                 taxes = invoice_line_id.tax_ids
    #                 tax_values = [price_subtotal_calc * tax['amount'] / 100 for tax in taxes]
    #                 tax_values = [round(value, 2) for value in tax_values]
    #                 tax_info = dict()

    #                 for tax in invoice_line_id.tax_ids:
    #                     if '-' not in str(tax.amount):
    #                         # Inicializa contador a cero para cada ID de impuesto
    #                         if tax.codigo_fe_dian not in tax_info:
    #                             tax_info[tax.codigo_fe_dian] = dict()
    #                             tax_info[tax.codigo_fe_dian]['total'] = 0
    #                             tax_info[tax.codigo_fe_dian]['info'] = dict()

    #                         # Suma al total de cada c??digo, y a??ade informaci??n por cada tarifa para cada l??nea.
    #                         if invoice_line_id.price_subtotal != 0:
    #                             price_subtotal_calc = invoice_line_id.price_subtotal
    #                         else:
    #                             taxes = False
    #                             if invoice_line_id.tax_line_id:
    #                                 taxes = invoice_line_id.tax_line_id.compute_all(invoice_line_id.line_price_reference, invoice_line_id.currency_id, invoice_line_id.quantity,product=invoice_line_id.product_id,partner=self.partner_id)
    #                             price_subtotal_calc = taxes['total_excluded'] if taxes else invoice_line_id.quantity * invoice_line_id.line_price_reference

    #                         total_impuestos += round(price_subtotal_calc * tax['amount'] / 100, 2)
    #                         if tax.amount not in tax_info[tax.codigo_fe_dian]['info']:
    #                             aux_total = tax_info[tax.codigo_fe_dian]['total']
    #                             aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                             aux_total = round(aux_total, 2)
    #                             tax_info[tax.codigo_fe_dian]['total'] = aux_total

    #                             tax_info[tax.codigo_fe_dian]['info'][tax.amount] = {
    #                                 'taxable_amount': price_subtotal_calc,
    #                                 'value': round(price_subtotal_calc * tax['amount'] / 100, 2),
    #                                 'technical_name': tax.tipo_impuesto_id.name,
    #                             }
    #                         else:
    #                             aux_tax = tax_info[tax.codigo_fe_dian]['info'][tax.amount]['value']
    #                             aux_total = tax_info[tax.codigo_fe_dian]['total']
    #                             aux_taxable = tax_info[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount']
    #                             aux_tax = aux_tax + price_subtotal_calc * tax['amount'] / 100
    #                             aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                             aux_taxable = aux_taxable + price_subtotal_calc
    #                             aux_tax = round(aux_tax, 2)
    #                             aux_total = round(aux_total, 2)
    #                             aux_taxable = round(aux_taxable, 2)
    #                             tax_info[tax.codigo_fe_dian]['info'][tax.amount]['value'] = aux_tax
    #                             tax_info[tax.codigo_fe_dian]['total'] = aux_total
    #                             tax_info[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount'] = aux_taxable
                                
    #                 if invoice_line_id.discount:
    #                     discount_line = invoice_line_id.price_unit * invoice_line_id.quantity * invoice_line_id.discount / 100
    #                     discount_line = round(discount_line, 2)
    #                     discount_percentage = invoice_line_id.discount
    #                     base_discount = invoice_line_id.price_unit * invoice_line_id.quantity
    #                 else:
    #                     discount_line = 0
    #                     discount_percentage = 0
    #                     base_discount = 0
    #                 mapa_line={
    #                     'id': index + contador,
    #                     'product_id': invoice_line_id.product_id.id,
    #                     'invoiced_quantity': invoice_line_id.quantity,
    #                     'uom_product_id': invoice_line_id.product_uom_id.codigo_fe_dian if invoice_line_id.product_uom_id else False,
    #                     'line_extension_amount': round(invoice_line_id.price_subtotal,2),
    #                     'item_description': saxutils.escape(invoice_line_id.name),
    #                     'price': round((invoice_line_id.price_subtotal + discount_line)/ invoice_line_id.quantity,2),
    #                     'total_amount_tax': round(invoice.amount_tax,2),
    #                     'tax_info': tax_info,
    #                     'discount': round(discount_line,2),
    #                     'discount_percentage': round(discount_percentage,2),
    #                     'base_discount': round(base_discount,2),
    #                     'discount_text': self.calcular_texto_descuento(invoice_line_id.invoice_discount_text),
    #                     'discount_code': invoice_line_id.invoice_discount_text,
    #                     'multiplier_discount': round(discount_percentage,2),
    #                     'line_trade_sample_price': invoice_line_id.line_trade_sample_price,
    #                     'line_price_reference': round((invoice_line_id.line_price_reference*invoice_line_id.quantity),2),
    #                 }
    #                 if invoice_line_id.move_id.usa_aiu and invoice_line_id.product_id and invoice_line_id.product_id.tipo_aiu:
    #                    mapa_line.update({'note': 'Contrato de servicios AIU por concepto de: ' + invoice_line_id.move_id.objeto_contrato})
    #                 invoice_lines.append(mapa_line)
                   
    #                 taxs = 0
    #                 if invoice_line_id.tax_ids.ids:
    #                     for item in invoice_line_id.tax_ids:
    #                         if not item.amount < 0:
    #                             taxs += 1
    #                             # si existe tax para una linea, entonces el price_subtotal
    #                             # de la linea se incluye en tax_exclusive_amount
    #                             if taxs > 1:  # si hay mas de un impuesto no se incluye  a la suma del tax_exclusive_amount
    #                                 pass
    #                             else:
    #                                 if invoice_line_id.price_subtotal != 0:
    #                                     tax_exclusive_amount += invoice_line_id.price_subtotal
    #                                 else:
    #                                     taxes = False
    #                                     if invoice_line_id.tax_line_id:
    #                                         taxes = invoice_line_id.tax_line_id.compute_all(invoice_line_id.line_price_reference, invoice_line_id.currency_id, invoice_line_id.quantity,product=invoice_line_id.product_id,partner=self.partner_id)
    #                                     price_subtotal_calc = taxes['total_excluded'] if taxes else invoice_line_id.quantity * invoice_line_id.line_price_reference
    #                                     tax_exclusive_amount += (price_subtotal_calc)
    #             else:
    #                 contador -= 1

    #         invoice.compute_discount()
    #         invoice.compute_charges_freight()
    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_primer_nombre.name]:
    #             invoice_customer_first_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_primer_nombre.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_primer_nombre.name]:
    #             invoice_customer_first_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_primer_nombre.name])
    #         else:
    #             invoice_customer_first_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_primer_apellido.name]:
    #             invoice_customer_family_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_primer_apellido.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_primer_apellido.name]:
    #             invoice_customer_family_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_primer_apellido.name])
    #         else:
    #             invoice_customer_family_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_segundo_apellido.name]:
    #             invoice_customer_family_last_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_segundo_apellido.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_apellido.name]:
    #             invoice_customer_family_last_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_apellido.name])
    #         else:
    #             invoice_customer_family_last_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_segundo_nombre.name]:
    #             invoice_customer_middle_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_segundo_nombre.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_nombre.name]:
    #             invoice_customer_middle_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_nombre.name])
    #         else:
    #             invoice_customer_middle_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_matricula_mercantil.name]:
    #             invoice_customer_commercial_registration = self.fe_tercero[ConfigFE.tercero_matricula_mercantil.name]
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_matricula_mercantil.name]:
    #             invoice_customer_commercial_registration = self.parent_fe_tercero[ConfigFE.padre_tercero_matricula_mercantil.name]
    #         else:
    #             invoice_customer_commercial_registration = 0

    #         if invoice.partner_id.fe_facturador:
    #             if type(self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name]).__name__ != 'list':
    #                 invoice_customer_tax_level_code = self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name]
    #             else:
    #                 invoice_customer_tax_level_code = ";".join(self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name])
    #         elif not invoice.partner_id.fe_facturador:
    #             if type(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name]).__name__ != 'list':
    #                 invoice_customer_tax_level_code = self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name]
    #             else:
    #                 invoice_customer_tax_level_code = ";".join(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name])

    #         duration_measure_array = []
    #         if len(self.invoice_payment_term_id.line_ids) > 1:
    #             for invoice_pay_term in self.invoice_payment_term_id.line_ids:
    #                 duration_measure_array.append(invoice_pay_term.days)
    #                 duration_measure = max(duration_measure_array)
    #         else:
    #             duration_measure = False


    #         invoice_fe_data = {
    #             'invoice_authorization': invoice.company_resolucion_id.number,
    #             'start_date': invoice.company_resolucion_id.fecha_inicial,
    #             'end_date': invoice.company_resolucion_id.fecha_final,
    #             'invoice_prefix': (
    #                 invoice.company_resolucion_id.prefijo
    #                 if invoice.company_resolucion_id.prefijo
    #                 else ''
    #             ),
    #             'authorization_from': self.company_resolucion_id.rango_desde,
    #             'authorization_to': self.company_resolucion_id.rango_hasta,
    #             'provider_id': self.fe_company[ConfigFE.company_nit.name],
    #             'software_id': self.company_id.fe_software_id,
    #             'software_security_code': software_security_code,
    #             'invoice_number': self.prefix_invoice_number(),
    #             'invoice_delivery_date': deliver_date.astimezone(pytz.timezone('America/Bogota')).strftime('%Y-%m-%d'),
    #             'invoice_delivery_time': deliver_date.astimezone(pytz.timezone('America/Bogota')).strftime('%H:%M:%S'),
    #             'invoice_discount':self.invoice_discount
    #                 if self.invoice_discount
    #                 else 0,
    #             'invoice_discount_percent':self.invoice_discount_percent
    #                 if self.invoice_discount_percent
    #                 else 0,
    #             'invoice_discount_text':self.calcular_texto_descuento(self.invoice_discount_text),
    #             'invoice_discount_code':self.invoice_discount_text
    #                 if self.invoice_discount_text
    #                 else 0,
    #             'invoice_charges_freight': self.invoice_charges_freight
    #                 if self.invoice_charges_freight
    #                 else 0,
    #             'invoice_charges_freight_percent': self.invoice_charges_freight_percent
    #                 if self.invoice_charges_freight_percent
    #                 else 0,
    #             'invoice_charges_freight_text': self.invoice_charges_freight_text if self.invoice_charges_freight_text else 'Fletes',
    #             'invoice_cufe': invoice.calcular_cufe(tax_total_values),
    #             'invoice_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'invoice_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_note': self.narration or '',
    #             'invoice_aiu': self.usa_aiu,
    #             # supplier
    #             'invoice_supplier_additional_account_id': self.company_id.partner_id.fe_es_compania,
    #             'invoice_supplier_document_type': self._tipo_de_documento(self.fe_company[ConfigFE.company_tipo_documento.name]),
    #             'invoice_supplier_identification': self.fe_company[ConfigFE.company_nit.name],
    #             'invoice_supplier_identification_digit': self.fe_company[ConfigFE.company_digito_verificacion.name],
    #             'invoice_supplier_party_name': saxutils.escape(invoice.company_id.name),
    #             'invoice_supplier_postal_code': (self.calcular_codigo_postal(self.fe_company[ConfigFE.company_postal.name]))
    #                 if not self.fe_sucursal
    #                 else (self.calcular_codigo_postal(self.fe_sucursal_data[ConfigFE.sucursal_postal.name])),
    #             'invoice_supplier_country_code': self.calcular_codigo_pais(self.fe_company[ConfigFE.company_pais.name])
    #                 if not self.fe_sucursal
    #                 else self.calcular_codigo_pais(self.fe_sucursal_data[ConfigFE.sucursal_pais.name]),
    #             'invoice_supplier_department': self.calcular_departamento(self.fe_company[ConfigFE.company_departamento.name])
    #                 if not self.fe_sucursal
    #                 else self.calcular_departamento(self.fe_sucursal_data[ConfigFE.sucursal_departamento.name]),
    #             'invoice_supplier_department_code': self.calcular_codigo_departamento(self.fe_company[ConfigFE.company_departamento.name])
    #                 if not self.fe_sucursal
    #                 else self.calcular_codigo_departamento(self.fe_sucursal_data[ConfigFE.sucursal_departamento.name]),
    #             'invoice_supplier_city': self.calcular_ciudad(self.fe_company[ConfigFE.company_ciudad.name])
    #                 if not self.fe_sucursal
    #                 else self.calcular_ciudad(self.fe_sucursal_data[ConfigFE.sucursal_ciudad.name]),
    #             'invoice_supplier_city_code': self.calcular_codigo_ciudad(self.fe_company[ConfigFE.company_ciudad.name])
    #                 if not self.fe_sucursal
    #                 else self.calcular_codigo_ciudad(self.fe_sucursal_data[ConfigFE.sucursal_ciudad.name]),
    #             'invoice_supplier_address_line': self.fe_company[ConfigFE.company_direccion.name]
    #                 if not self.fe_sucursal
    #                 else self.fe_sucursal_data[ConfigFE.sucursal_direccion.name],
    #             'invoice_supplier_tax_level_code':
    #                 self.fe_company[ConfigFE.company_responsabilidad_fiscal.name]
    #                 if type(self.fe_company[ConfigFE.company_responsabilidad_fiscal.name]).__name__ != 'list'
    #                 else ";".join(self.fe_company[ConfigFE.company_responsabilidad_fiscal.name]),
    #             'invoice_supplier_responsabilidad_tributaria': self.fe_company[ConfigFE.company_responsabilidad_tributaria.name],
    #             'invoice_supplier_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.fe_company[ConfigFE.company_responsabilidad_tributaria.name]),
    #             'invoice_supplier_commercial_registration':
    #                 self.fe_company[ConfigFE.company_matricula_mercantil.name]
    #                 if self.fe_company[ConfigFE.company_matricula_mercantil.name]
    #                 else 0,
    #             'invoice_supplier_phone': self.fe_company[ConfigFE.company_telefono.name]
    #                 if not self.fe_sucursal
    #                 else self.fe_sucursal_data[ConfigFE.sucursal_telefono.name],
    #             'invoice_supplier_email': self.fe_company[ConfigFE.company_email_from.name]
    #                 if not self.fe_sucursal
    #                 else self.fe_sucursal_data[ConfigFE.sucursal_to_email.name],
    #             # customer
    #             'invoice_customer_additional_account_id': self.fe_tercero[ConfigFE.tercero_es_compania.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name],
    #             'invoice_customer_document_type': self._tipo_de_documento(self.fe_tercero[ConfigFE.tercero_tipo_documento.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self._tipo_de_documento(self.parent_fe_tercero[ConfigFE.padre_tercero_tipo_documento.name]),
    #             'invoice_customer_identification': self.fe_tercero[ConfigFE.tercero_nit.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_nit.name],
    #             'invoice_customer_identification_digit': self.fe_tercero[ConfigFE.tercero_digito_verificacion.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_digito_verificacion.name],
    #             'invoice_customer_party_name': saxutils.escape(invoice.partner_id.name)
    #                 if invoice.partner_id.fe_facturador
    #                 else saxutils.escape(invoice.partner_id.parent_id.name),
    #             'invoice_customer_department': self.calcular_departamento(self.fe_tercero[ConfigFE.tercero_departamento.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_departamento(self.parent_fe_tercero[ConfigFE.padre_tercero_departamento.name]),
    #             'invoice_customer_department_code': self.calcular_codigo_departamento(self.fe_tercero[ConfigFE.tercero_departamento.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_codigo_departamento(self.parent_fe_tercero[ConfigFE.padre_tercero_departamento.name]),
    #             'invoice_customer_city': self.calcular_ciudad(self.fe_tercero[ConfigFE.tercero_ciudad.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_ciudad(self.parent_fe_tercero[ConfigFE.padre_tercero_ciudad.name]),
    #             'invoice_customer_city_code': self.calcular_codigo_ciudad(self.fe_tercero[ConfigFE.tercero_ciudad.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_codigo_ciudad(self.parent_fe_tercero[ConfigFE.padre_tercero_ciudad.name]),
    #             'invoice_customer_postal_code': (self.calcular_codigo_postal(self.fe_tercero[ConfigFE.tercero_postal.name]))
    #                 if invoice.partner_id.fe_facturador
    #                 else (self.calcular_codigo_postal(self.parent_fe_tercero[ConfigFE.padre_tercero_postal.name])),
    #             'invoice_customer_country': self.calcular_pais(self.fe_tercero[ConfigFE.tercero_pais.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_pais(self.parent_fe_tercero[ConfigFE.padre_tercero_pais.name]),
    #             'invoice_customer_country_code': self.calcular_codigo_pais(self.fe_tercero[ConfigFE.tercero_pais.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_codigo_pais(self.parent_fe_tercero[ConfigFE.padre_tercero_pais.name]),
    #             'invoice_customer_address_line': self.fe_tercero[ConfigFE.tercero_direccion.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_direccion.name],
    #             'invoice_customer_is_company': self.fe_tercero[ConfigFE.tercero_es_compania.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name],
    #             'invoice_customer_first_name': invoice_customer_first_name,
    #             'invoice_customer_family_name': invoice_customer_family_name,
    #             'invoice_customer_family_last_name':invoice_customer_family_last_name,
    #             'invoice_customer_middle_name':invoice_customer_middle_name,
    #             'invoice_customer_phone': self.fe_tercero[ConfigFE.tercero_telefono.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_telefono.name],
    #             'invoice_customer_commercial_registration':invoice_customer_commercial_registration,
    #             'invoice_customer_email': self.fe_tercero[ConfigFE.tercero_to_email.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_to_email.name],
    #             'invoice_customer_tax_level_code':invoice_customer_tax_level_code,
    #             'invoice_customer_responsabilidad_tributaria':self.fe_tercero[ConfigFE.tercero_responsabilidad_tributaria.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_tributaria.name],
    #             'invoice_customer_responsabilidad_tributaria_text':self.calcular_texto_responsabilidad_tributaria(self.fe_tercero[ConfigFE.tercero_responsabilidad_tributaria.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_texto_responsabilidad_tributaria(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_tributaria.name]),
    #             # legal monetary total
    #             'line_extension_amount': '{:.2f}'.format(invoice.amount_untaxed),
    #             'tax_exclusive_amount': '{:.2f}'.format(tax_exclusive_amount),
    #             'tax_inclusive_amount': '{:.2f}'.format(invoice.amount_untaxed + total_impuestos),
    #             'payable_amount': '{:.2f}'.format(invoice.amount_total + invoice.total_withholding_amount),
    #             #    if self.currency_id.name=='COP'
    #             #    else '{:.2f}'.format(invoice.amount_total + invoice.total_withholding_amount + invoice.invoice_charges_freight - invoice.invoice_discount),
    #             'payable_amount_discount': '{:.2f}'.format(invoice.amount_total + invoice.invoice_discount - invoice.invoice_charges_freight + invoice.total_withholding_amount),
    #             #    if self.currency_id.name == 'COP'
    #             #    else '{:.2f}'.format(invoice.amount_total + invoice.total_withholding_amount),
    #             # invoice lines
    #             'invoice_lines': invoice_lines,

    #             'tax_total': tax_values,
    #             'tax_total_values': tax_total_values,
    #             'ret_total_values': ret_total_values,
    #             'date_due': invoice.invoice_date_due,
    #             # Info validaci??n previa
    #             'payment_means_id': self.forma_de_pago,
    #             'payment_means_code': self.payment_mean_id.codigo_fe_dian,
    #             'payment_id': self.payment_mean_id.nombre_tecnico_dian,
    #             'reference_event_code': self.invoice_payment_term_id.codigo_fe_dian,
    #             'duration_measure': duration_measure  if duration_measure else self.invoice_payment_term_id.line_ids.days,
    #             'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'order_reference': self.order_reference,
    #             'order_reference_date': self.order_reference_date,
    #             'additional_document_reference': self.additional_document_reference,
    #             'despatch_document_reference': self.despatch_document_reference,
    #             'despatch_document_reference_date': self.despatch_document_reference_date,
    #             'refacturapt_document_reference': self.refacturapt_document_reference,
    #             'refacturapt_document_reference_date': self.refacturapt_document_reference_date,
    #             'invoice_trade_sample':self.invoice_trade_sample,
    #         }
    #         if (invoice.amount_residual-invoice.invoice_charges_freight_view)!=invoice.amount_total:
    #             invoice_fe_data.update({'prepaid_amount': invoice.amount_total-invoice.amount_residual,"invoice_prepaids":invoice_prepaids})

    #         ##Validaci??n de C??digos Postales
    #         if invoice.partner_id.fe_facturador and not self.fe_tercero[ConfigFE.tercero_postal.name]:
    #             raise ValidationError("El cliente no tiene parametrizado C??digo Postal")
    #         if not invoice.partner_id.fe_facturador and not self.parent_fe_tercero[ConfigFE.padre_tercero_postal.name]:
    #             raise ValidationError("El padre del cliente no tiene parametrizado C??digo Postal")
    #         if not self.fe_company[ConfigFE.company_postal.name]:
    #             raise ValidationError("La Compa??ia no tiene parametrizado C??digo Postal")
    #         if self.fe_sucursal and not self.fe_sucursal_data[ConfigFE.sucursal_postal.name]:
    #             raise ValidationError("La sucursal no tiene parametrizado C??digo Postal")
    #         ##Fin de validaci??n

    #         if invoice.partner_id.fe_facturador:
    #             if self.fe_tercero[ConfigFE.tercero_es_compania.name] == '1':
    #                 invoice_fe_data['invoice_registration_name'] = saxutils.escape(self.fe_tercero[ConfigFE.tercero_razon_social.name])
    #             elif self.fe_tercero[ConfigFE.tercero_es_compania.name] == '2':
    #                 invoice_fe_data['invoice_customer_is_company'] = saxutils.escape(self.fe_tercero[ConfigFE.tercero_es_compania.name])
    #         else:
    #             if self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name] == '1':
    #                 invoice_fe_data['invoice_registration_name'] = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_razon_social.name])
    #             elif self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name] == '2':
    #                 invoice_fe_data['invoice_customer_is_company'] = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name])


    #         invoice_fe_data['currency_id'] = self.currency_id.name


    #         if self.es_factura_exportacion:
    #             invoice_fe_data['calculation_rate'] = self.env.context['value_rate_exchange'] if 'value_check_rate' in self.env.context and self.env.context['value_check_rate'] else round(1 / self.currency_id.rate, 2)
    #             invoice_fe_data['rate_date'] = self.date
    #             invoice_fe_data['invoice_customer_country'] = self.partner_id.country_id.iso_name
    #             invoice_fe_data['invoice_incoterm_code'] = self.invoice_incoterm_id.code
    #             invoice_fe_data['invoice_incoterm_description'] = self.invoice_incoterm_id.name
    #             xml_template = self.get_template_str('../templates/export.xml')
    #             export_template = Template(xml_template)
    #             output = export_template.render(invoice_fe_data)
    #         else:
    #             if self.currency_id.name != 'COP':
    #                 invoice_fe_data['calculation_rate'] = self.env.context['value_rate_exchange'] if 'value_check_rate' in self.env.context and self.env.context['value_check_rate'] else round(1 / self.currency_id.rate, 2)
    #                 invoice_fe_data['rate_date'] = self.date
    #             xml_template = self.get_template_str('../templates/invoice.xml')
    #             invoice_template = Template(xml_template)
    #             output = invoice_template.render(invoice_fe_data)

    #         return output
    #     except Exception as e:
    #         raise ValidationError(
    #             "Error validando la factura : {}".format(e)
    #         )

    # # endregion
    # # region calcular_ciudad

    # def calcular_ciudad(self, objeto):
    #     return objeto.city_name

    # # endregion
    # # region calcular_ciudad_tercero
    # def calcular_ciudad_tercero(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     if ConfigFE.tercero_ciudad.name in self.fe_tercero:
    #         return self.calcular_ciudad(self.fe_tercero[ConfigFE.tercero_ciudad.name])
    #     else:
    #         return ''

    # # endregion
    # # region calcular_ciudad_padre_tercero
    # def calcular_ciudad_padre_tercero(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     if ConfigFE.padre_tercero_ciudad.name in self.parent_fe_tercero:
    #         return self.calcular_ciudad(self.parent_fe_tercero[ConfigFE.padre_tercero_ciudad.name])
    #     else:
    #         return ''

    # # endregion
    # # region calcular_ciudad_company
    # def calcular_ciudad_company(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_ciudad(self.fe_company[ConfigFE.company_ciudad.name])

    # # endregion
    # # region calcular_ciudad_sucursal
    # def calcular_ciudad_sucursal(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_ciudad(self.fe_sucursal_data[ConfigFE.sucursal_ciudad.name])

    # # endregion
    # # region calcular_codigo_ciudad
    # def calcular_codigo_ciudad(self, objeto):
    #     return objeto.city_code

    # # endregion
    # # region calcular_pais
    # def calcular_pais(self, objeto):
    #     return objeto.iso_name

    # # endregion
    # # region calcular_codigo_postal
    # def calcular_codigo_postal(self, objeto):
    #     return objeto.name

    # # endregion
    # # region calcular_pais_tercero
    # def calcular_pais_tercero(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_pais(self.fe_tercero[ConfigFE.tercero_pais.name])

    # # endregion
    # # region calcular_pais_padre_tercero
    # def calcular_pais_padre_tercero(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_pais(self.parent_fe_tercero[ConfigFE.padre_tercero_pais.name])

    # # endregion
    # # region calcular_pais_company
    # def calcular_pais_company(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_pais(self.fe_company[ConfigFE.company_pais.name])

    # # endregion
    # # region calcular_pais_sucursal
    # def calcular_pais_sucursal(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_pais(self.fe_sucursal_data[ConfigFE.sucursal_pais.name])

    # # endregion
    # # region calcular_codigo_pais
    # def calcular_codigo_pais(self, objeto):
    #     return objeto.code

    # # endregion
    # # region calcular_departamento
    # def calcular_departamento(self, objeto):
    #     return objeto.name

    # # endregion
    # # region calcular_departamento_tercero
    # def calcular_departamento_tercero(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_departamento(self.fe_tercero[ConfigFE.tercero_departamento.name])

    # # endregion
    # # region calcular_departamento_padre_tercero
    # def calcular_departamento_padre_tercero(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_departamento(self.parent_fe_tercero[ConfigFE.padre_tercero_departamento.name])

    # # endregion
    # # region calcular_departamento_company
    # def calcular_departamento_company(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_departamento(self.fe_company[ConfigFE.company_departamento.name])

    # # endregion
    # # region calcular_departamento_sucursal
    # def calcular_departamento_sucursal(self):
    #     vector = self._load_config_data()
    #     self.fe_company = vector[0]
    #     self.fe_tercero = vector[1]
    #     self.fe_sucursal_data = vector[2]
    #     self.parent_fe_tercero = vector[3]
    #     return self.calcular_departamento(self.fe_sucursal_data[ConfigFE.sucursal_departamento.name])

    # # endregion
    # # region calcular_codigo_departamento
    # def calcular_codigo_departamento(self, objeto):
    #     return objeto.state_code

    # # endregion
    # # region _get_value_config
    # def _get_value_config(self, field_name):
    #     config_fe = self._get_config()

    #     return config_fe.get_value(
    #         field_name=field_name,
    #         obj_id=self.id
    #     )

    # # endregion
    # # region generar_creditnote_xml
    # def generar_creditnote_xml(self):
    #     self.fe_company, self.fe_tercero, self.fe_sucursal_data, self.parent_fe_tercero = self._load_config_data()
    #     self.fecha_xml = datetime.datetime.combine(self.invoice_date, datetime.datetime.now().time())
    #     create_date = self._str_to_datetime(self.fecha_xml)
    #     deliver_date = self._str_to_datetime(self.fecha_entrega)
    #     invoice = self

    #     key_data = '{}{}{}'.format(
    #         invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin, invoice.prefix_invoice_number()
    #     )
    #     sha384 = hashlib.sha384()
    #     sha384.update(key_data.encode())
    #     software_security_code = sha384.hexdigest()

    #     reconciled_vals = self._get_reconciled_info_JSON_values()
    #     invoice_prepaids = []
    #     for reconciled_val in reconciled_vals:
    #         move_line_pago = self.env['account.move.line'].sudo().search([('id', '=', reconciled_val.get('payment_id'))])
    #         mapa_prepaid = {
    #             'id': reconciled_val.get('payment_id'),
    #             'paid_amount': reconciled_val.get('amount'),
    #             'currency_id': str(self.currency_id.name),
    #             'refacturaved_date': str(move_line_pago.date),
    #             'paid_date': str(move_line_pago.date),
    #             'paid_time': '12:00:00'
    #         }
    #         invoice_prepaids.append(mapa_prepaid)

    #     creditnote_lines = []

    #     tax_exclusive_amount = 0
    #     self.total_withholding_amount = 0.0
    #     tax_total_values = {}
    #     ret_total_values = {}

    #     # Bloque de c??digo para imitar la estructura requerida por el XML de la DIAN para los totales externos
    #     # a las l??neas de la factura.
    #     for line_id in self.invoice_line_ids:
    #         for tax in line_id.tax_ids:
    #             if '-' not in str(tax.amount):
    #                 # Inicializa contador a cero para cada ID de impuesto
    #                 if tax.codigo_fe_dian not in tax_total_values:
    #                     tax_total_values[tax.codigo_fe_dian] = dict()
    #                     tax_total_values[tax.codigo_fe_dian]['total'] = 0
    #                     tax_total_values[tax.codigo_fe_dian]['info'] = dict()

    #                 # Suma al total de cada c??digo, y a??ade informaci??n por cada tarifa.
    #                 if line_id.price_subtotal != 0:
    #                     price_subtotal_calc = line_id.price_subtotal
    #                 else:
    #                     taxes = False
    #                     if line_id.tax_line_id:
    #                         taxes = line_id.tax_line_id.compute_all(line_id.line_price_reference, line_id.currency_id, line_id.quantity,product=line_id.product_id,partner=self.partner_id)
    #                     price_subtotal_calc = taxes['total_excluded'] if taxes else line_id.quantity * line_id.line_price_reference
    #                 if tax.amount not in tax_total_values[tax.codigo_fe_dian]['info']:


    #                     aux_total = tax_total_values[tax.codigo_fe_dian]['total']
    #                     aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                     aux_total = round(aux_total, 2)
    #                     tax_total_values[tax.codigo_fe_dian]['total'] = aux_total
    #                     tax_total_values[tax.codigo_fe_dian]['info'][tax.amount] = {
    #                         'taxable_amount': (price_subtotal_calc),
    #                         'value': round(price_subtotal_calc * tax['amount'] / 100, 2),
    #                         'technical_name': tax.tipo_impuesto_id.name,
    #                     }

    #                 else:
    #                     aux_tax = tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['value']
    #                     aux_total = tax_total_values[tax.codigo_fe_dian]['total']
    #                     aux_taxable = tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount']
    #                     aux_tax = aux_tax + price_subtotal_calc * tax['amount'] / 100
    #                     aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                     aux_taxable = aux_taxable + price_subtotal_calc
    #                     aux_tax = round(aux_tax, 2)
    #                     aux_total = round(aux_total, 2)
    #                     aux_taxable = round(aux_taxable, 2)
    #                     tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['value'] = aux_tax
    #                     tax_total_values[tax.codigo_fe_dian]['total'] = aux_total
    #                     tax_total_values[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount'] = aux_taxable
                        
    #             else:
    #                 # Inicializa contador a cero para cada ID de impuesto
    #                 if tax.codigo_fe_dian not in ret_total_values:
    #                     ret_total_values[tax.codigo_fe_dian] = dict()
    #                     ret_total_values[tax.codigo_fe_dian]['total'] = 0
    #                     ret_total_values[tax.codigo_fe_dian]['info'] = dict()

    #                 # Suma al total de cada c??digo, y a??ade informaci??n por cada tarifa.
    #                 if line_id.price_subtotal != 0:
    #                     price_subtotal_calc = line_id.price_subtotal
    #                 else:
    #                     taxes = False
    #                     if line_id.tax_line_id:
    #                         taxes = line_id.tax_line_id.compute_all(line_id.line_price_reference, line_id.currency_id, line_id.quantity,product=line_id.product_id,partner=self.partner_id)
    #                     price_subtotal_calc = taxes['total_excluded'] if taxes else line_id.quantity * line_id.line_price_reference
    #                 if abs(tax.amount) not in ret_total_values[tax.codigo_fe_dian]['info']:
                        
    #                     aux_total = ret_total_values[tax.codigo_fe_dian]['total']
    #                     aux_total = aux_total + price_subtotal_calc * abs(tax['amount']) / 100
    #                     aux_total = round(aux_total, 2)
    #                     ret_total_values[tax.codigo_fe_dian]['total'] = abs(aux_total)

    #                     ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)] = {
    #                         'taxable_amount': abs(price_subtotal_calc),
    #                         'value': abs(round(price_subtotal_calc * abs(tax['amount']) / 100, 2)),
    #                         'technical_name': tax.tipo_impuesto_id.name,
    #                     }
                        
    #                 else:
                        
    #                     aux_tax = ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['value']
    #                     aux_total = ret_total_values[tax.codigo_fe_dian]['total']
    #                     aux_taxable = ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['taxable_amount']
    #                     aux_tax = aux_tax + line_id.price_subtotal * abs(tax['amount']) / 100
    #                     aux_total = aux_total + line_id.price_subtotal * abs(tax['amount']) / 100
    #                     aux_taxable = aux_taxable + line_id.price_subtotal
    #                     aux_tax = round(aux_tax, 2)
    #                     aux_total = round(aux_total, 2)
    #                     aux_taxable = round(aux_taxable, 2)
    #                     ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['value'] = abs(aux_tax)
    #                     ret_total_values[tax.codigo_fe_dian]['total'] = abs(aux_total)
    #                     ret_total_values[tax.codigo_fe_dian]['info'][abs(tax.amount)]['taxable_amount'] = abs(aux_taxable)
                        
    #     for ret in ret_total_values.items():
    #         self.total_withholding_amount += abs(ret[1]['total'])

    #     contador = 0
    #     total_impuestos = 0
    #     for index, invoice_line_id in enumerate(self.invoice_line_ids):
    #         if not invoice_line_id.product_id.enable_charges and invoice_line_id.price_unit>=0:
    #             if invoice_line_id.price_subtotal != 0:
    #                 price_subtotal_calc = invoice_line_id.price_subtotal
    #             else:
    #                 taxes = False
    #                 if invoice_line_id.tax_line_id:
    #                     taxes = invoice_line_id.tax_line_id.compute_all(invoice_line_id.line_price_reference, invoice_line_id.currency_id, invoice_line_id.quantity,product=invoice_line_id.product_id,partner=self.partner_id)
    #                 price_subtotal_calc = taxes['total_excluded'] if taxes else invoice_line_id.quantity * invoice_line_id.line_price_reference

    #             taxes = invoice_line_id.tax_ids
    #             tax_values = [price_subtotal_calc * tax['amount'] / 100 for tax in taxes]
    #             tax_values = [round(value, 2) for value in tax_values]
    #             tax_info = dict()

    #             for tax in invoice_line_id.tax_ids:
    #                 if '-' not in str(tax.amount):
    #                     # Inicializa contador a cero para cada ID de impuesto
    #                     if tax.codigo_fe_dian not in tax_info:
    #                         tax_info[tax.codigo_fe_dian] = dict()
    #                         tax_info[tax.codigo_fe_dian]['total'] = 0
    #                         tax_info[tax.codigo_fe_dian]['info'] = dict()

    #                     # Suma al total de cada c??digo, y a??ade informaci??n por cada tarifa para cada l??nea.
    #                     if invoice_line_id.price_subtotal != 0:
    #                         price_subtotal_calc = invoice_line_id.price_subtotal
    #                     else:
    #                         taxes = False
    #                         if invoice_line_id.tax_line_id:
    #                             taxes = invoice_line_id.tax_line_id.compute_all(invoice_line_id.line_price_reference, invoice_line_id.currency_id, invoice_line_id.quantity,product=invoice_line_id.product_id,partner=self.partner_id)
    #                         price_subtotal_calc = taxes['total_excluded'] if taxes else invoice_line_id.quantity * invoice_line_id.line_price_reference

    #                     total_impuestos += round(price_subtotal_calc * tax['amount'] / 100, 2)
    #                     if tax.amount not in tax_info[tax.codigo_fe_dian]['info']:
                            
    #                         aux_total = tax_info[tax.codigo_fe_dian]['total']
    #                         aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                         aux_total = round(aux_total, 2)
    #                         tax_info[tax.codigo_fe_dian]['total'] = aux_total

    #                         tax_info[tax.codigo_fe_dian]['info'][tax.amount] = {
    #                             'taxable_amount': price_subtotal_calc,
    #                             'value': round(price_subtotal_calc* tax['amount'] / 100, 2),
    #                             'technical_name': tax.tipo_impuesto_id.name,
    #                         }
                            
    #                     else:
                            
    #                         aux_tax = tax_info[tax.codigo_fe_dian]['info'][tax.amount]['value']
    #                         aux_total = tax_info[tax.codigo_fe_dian]['total']
    #                         aux_taxable = tax_info[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount']
    #                         aux_tax = aux_tax + price_subtotal_calc * tax['amount'] / 100
    #                         aux_total = aux_total + price_subtotal_calc * tax['amount'] / 100
    #                         aux_taxable = aux_taxable + price_subtotal_calc
    #                         aux_tax = round(aux_tax, 2)
    #                         aux_total = round(aux_total, 2)
    #                         aux_taxable = round(aux_taxable, 2)
    #                         tax_info[tax.codigo_fe_dian]['info'][tax.amount]['value'] = aux_tax
    #                         tax_info[tax.codigo_fe_dian]['total'] = aux_total
    #                         tax_info[tax.codigo_fe_dian]['info'][tax.amount]['taxable_amount'] = aux_taxable
                            
    #             if invoice_line_id.discount:
    #                 discount_line = invoice_line_id.price_unit * invoice_line_id.quantity * invoice_line_id.discount / 100
    #                 discount_line = round(discount_line, 2)
    #                 discount_percentage = invoice_line_id.discount
    #                 base_discount = invoice_line_id.price_unit * invoice_line_id.quantity
    #             else:
    #                 discount_line = 0
    #                 discount_percentage = 0
    #                 base_discount = 0

    #             mapa_line={
    #                 'id': index + 1,
    #                 'product_id': invoice_line_id.product_id.id,
    #                 'credited_quantity': invoice_line_id.quantity,
    #                 'uom_product_id': invoice_line_id.product_uom_id.codigo_fe_dian if invoice_line_id.product_uom_id else False,
    #                 'line_extension_amount': round(invoice_line_id.price_subtotal,2),
    #                 'item_description': saxutils.escape(invoice_line_id.name),
    #                 'price': round((invoice_line_id.price_subtotal + discount_line)/ invoice_line_id.quantity,2),
    #                 'total_amount_tax': round(invoice.amount_tax,2),
    #                 'tax_info': tax_info,
    #                 'discount': round(discount_line,2),
    #                 'discount_text': self.calcular_texto_descuento(invoice_line_id.invoice_discount_text),
    #                 'discount_code': invoice_line_id.invoice_discount_text,
    #                 'discount_percentage': round(discount_percentage,2),
    #                 'base_discount': round(base_discount,2),
    #                 'multiplier_discount': discount_percentage,
    #                 'line_trade_sample_price': invoice_line_id.line_trade_sample_price,
    #                 'line_price_reference': round((invoice_line_id.line_price_reference * invoice_line_id.quantity),2),
    #             }
    #             if invoice_line_id.move_id.usa_aiu and invoice_line_id.product_id and invoice_line_id.product_id.tipo_aiu:
    #                 mapa_line.update({'note': 'Contrato de servicios AIU por concepto de: ' + invoice_line_id.move_id.objeto_contrato})
    #             creditnote_lines.append(mapa_line)

    #             taxs = 0
    #             if invoice_line_id.tax_ids.ids:
    #                 for item in invoice_line_id.tax_ids:
    #                     if not item.amount < 0:
    #                         taxs += 1
    #                         # si existe tax para una linea, entonces el price_subtotal
    #                         # de la linea se incluye en tax_exclusive_amount
    #                         if taxs > 1:  # si hay mas de un impuesto no se incluye  a la suma del tax_exclusive_amount
    #                             pass
    #                         else:
    #                             if invoice_line_id.price_subtotal != 0:
    #                                 tax_exclusive_amount += invoice_line_id.price_subtotal
    #                             else:
    #                                 taxes = False
    #                                 if invoice_line_id.tax_line_id:
    #                                     taxes = invoice_line_id.tax_line_id.compute_all(invoice_line_id.line_price_reference, invoice_line_id.currency_id, invoice_line_id.quantity,product=invoice_line_id.product_id,partner=self.partner_id)
    #                                 price_subtotal_calc = taxes['total_excluded'] if taxes else invoice_line_id.quantity * invoice_line_id.line_price_reference
    #                                 tax_exclusive_amount += (price_subtotal_calc)
    #         else:
    #             contador -= 1

    #     invoice.compute_discount()
    #     invoice.compute_charges_freight()

    #     if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_primer_nombre.name]:
    #         invoice_customer_first_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_primer_nombre.name])
    #     elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_primer_nombre.name]:
    #         invoice_customer_first_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_primer_nombre.name])
    #     else:
    #         invoice_customer_first_name = ''

    #     if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_primer_apellido.name]:
    #         invoice_customer_family_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_primer_apellido.name])
    #     elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_primer_apellido.name]:
    #         invoice_customer_family_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_primer_apellido.name])
    #     else:
    #         invoice_customer_family_name = ''

    #     if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_segundo_apellido.name]:
    #         invoice_customer_family_last_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_segundo_apellido.name])
    #     elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_apellido.name]:
    #         invoice_customer_family_last_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_apellido.name])
    #     else:
    #         invoice_customer_family_last_name = ''

    #     if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_segundo_nombre.name]:
    #         invoice_customer_middle_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_segundo_nombre.name])
    #     elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_nombre.name]:
    #         invoice_customer_middle_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_nombre.name])
    #     else:
    #         invoice_customer_middle_name = ''

    #     if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_matricula_mercantil.name]:
    #         invoice_customer_commercial_registration = self.fe_tercero[ConfigFE.tercero_matricula_mercantil.name]
    #     elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_matricula_mercantil.name]:
    #         invoice_customer_commercial_registration = self.parent_fe_tercero[ConfigFE.padre_tercero_matricula_mercantil.name]
    #     else:
    #         invoice_customer_commercial_registration = 0

    #     if invoice.partner_id.fe_facturador:
    #         if type(self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name]).__name__ != 'list':
    #             invoice_customer_tax_level_code = self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name]
    #         else:
    #             invoice_customer_tax_level_code = ";".join(self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name])
    #     elif not invoice.partner_id.fe_facturador:
    #         if type(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name]).__name__ != 'list':
    #             invoice_customer_tax_level_code = self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name]
    #         else:
    #             invoice_customer_tax_level_code = ";".join(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name])

    #     duration_measure_array = []
    #     if len(self.invoice_payment_term_id.line_ids) > 1:
    #         for invoice_pay_term in self.invoice_payment_term_id.line_ids:
    #             duration_measure_array.append(invoice_pay_term.days)
    #             duration_measure = max(duration_measure_array)
    #     else:
    #         duration_measure = False


    #     creditnote_fe_data = {
    #         'invoice_prefix_nc': (
    #             invoice.company_resolucion_id.prefijo_nota
    #             if invoice.company_resolucion_id.prefijo_nota
    #             else ''
    #         ),
    #         'invoice_prefix_nd': (
    #             invoice.company_resolucion_id.prefijo
    #             if invoice.company_resolucion_id.prefijo
    #             else ''
    #         ),
    #         'provider_id': self.fe_company[ConfigFE.company_nit.name],
    #         'software_id': self.company_id.fe_software_id,
    #         'software_security_code': software_security_code,
    #         'invoice_number': self.prefix_invoice_number(),
    #         'invoice_delivery_date': deliver_date.astimezone(pytz.timezone('America/Bogota')).strftime('%Y-%m-%d'),
    #         'invoice_delivery_time': deliver_date.astimezone(pytz.timezone('America/Bogota')).strftime('%H:%M:%S'),
    #         'invoice_discount':self.invoice_discount
    #             if self.invoice_discount
    #             else 0,
    #         'invoice_discount_percent':self.invoice_discount_percent
    #             if self.invoice_discount_percent
    #             else 0,
    #         'invoice_discount_text':self.calcular_texto_descuento(self.invoice_discount_text),
    #         'invoice_discount_code':self.invoice_discount_text
    #             if self.invoice_discount_text
    #             else 0,
    #         'invoice_charges_freight': self.invoice_charges_freight
    #             if self.invoice_charges_freight
    #             else 0,
    #         'invoice_charges_freight_percent': self.invoice_charges_freight_percent
    #             if self.invoice_charges_freight_percent
    #             else 0,
    #         'invoice_charges_freight_text': self.invoice_charges_freight_text if self.invoice_charges_freight_text else 'Fletes',
    #         'creditnote_cufe': self.calcular_cufe(tax_total_values),
    #         'invoice_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #         'invoice_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #         'invoice_note': invoice.name if invoice.name else '',
    #         'invoice_aiu': self.usa_aiu,
    #         'credit_note_reason': invoice.reversed_entry_id.narration or '',
    #         'billing_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #         # supplier
    #         'invoice_supplier_additional_account_id': self.company_id.partner_id.fe_es_compania,
    #         'invoice_supplier_document_type': self._tipo_de_documento(self.fe_company[ConfigFE.company_tipo_documento.name]),
    #         'invoice_supplier_identification': self.fe_company[ConfigFE.company_nit.name],
    #         'invoice_supplier_identification_digit': self.fe_company[ConfigFE.company_digito_verificacion.name],
    #         'invoice_supplier_party_name': saxutils.escape(invoice.company_id.name),
    #         'invoice_supplier_postal_code': (self.calcular_codigo_postal(self.fe_company[ConfigFE.company_postal.name]))
    #             if not self.fe_sucursal
    #             else (self.calcular_codigo_postal(self.fe_sucursal_data[ConfigFE.sucursal_postal.name])),
    #         'invoice_supplier_country_code': self.calcular_codigo_pais(self.fe_company[ConfigFE.company_pais.name])
    #             if not self.fe_sucursal
    #             else self.calcular_codigo_pais(self.fe_sucursal_data[ConfigFE.sucursal_pais.name]),
    #         'invoice_supplier_department': self.calcular_departamento(self.fe_company[ConfigFE.company_departamento.name])
    #             if not self.fe_sucursal
    #             else self.calcular_departamento(self.fe_sucursal_data[ConfigFE.sucursal_departamento.name]),
    #         'invoice_supplier_department_code': self.calcular_codigo_departamento(self.fe_company[ConfigFE.company_departamento.name])
    #             if not self.fe_sucursal
    #             else self.calcular_codigo_departamento(self.fe_sucursal_data[ConfigFE.sucursal_departamento.name]),
    #         'invoice_supplier_city': self.calcular_ciudad(self.fe_company[ConfigFE.company_ciudad.name])
    #             if not self.fe_sucursal
    #             else self.calcular_ciudad(self.fe_sucursal_data[ConfigFE.sucursal_ciudad.name]),
    #         'invoice_supplier_city_code': self.calcular_codigo_ciudad(self.fe_company[ConfigFE.company_ciudad.name])
    #             if not self.fe_sucursal
    #             else self.calcular_codigo_ciudad(self.fe_sucursal_data[ConfigFE.sucursal_ciudad.name]),
    #         'invoice_supplier_address_line': self.fe_company[ConfigFE.company_direccion.name]
    #             if not self.fe_sucursal
    #             else self.fe_sucursal_data[ConfigFE.sucursal_direccion.name],
    #         'invoice_supplier_tax_level_code':
    #             self.fe_company[ConfigFE.company_responsabilidad_fiscal.name]
    #             if type(self.fe_company[ConfigFE.company_responsabilidad_fiscal.name]).__name__!='list'
    #             else ";".join(self.fe_company[ConfigFE.company_responsabilidad_fiscal.name]),
    #         'invoice_supplier_responsabilidad_tributaria':self.fe_company[ConfigFE.company_responsabilidad_tributaria.name],
    #         'invoice_supplier_responsabilidad_tributaria_text':self.calcular_texto_responsabilidad_tributaria(self.fe_company[ConfigFE.company_responsabilidad_tributaria.name]),
    #         'invoice_supplier_commercial_registration':
    #             self.fe_company[ConfigFE.company_matricula_mercantil.name]
    #             if self.fe_company[ConfigFE.company_matricula_mercantil.name]
    #             else 0,
    #         'invoice_supplier_phone': self.fe_company[ConfigFE.company_telefono.name]
    #             if not self.fe_sucursal
    #             else self.fe_sucursal_data[ConfigFE.sucursal_telefono.name],
    #         'invoice_supplier_email': self.fe_company[ConfigFE.company_email_from.name]
    #             if not self.fe_sucursal
    #             else self.fe_sucursal_data[ConfigFE.sucursal_to_email.name],
    #         # customer
    #         'invoice_customer_additional_account_id': self.fe_tercero[ConfigFE.tercero_es_compania.name]
    #             if invoice.partner_id.fe_facturador
    #             else self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name],
    #         'invoice_customer_document_type': self._tipo_de_documento(self.fe_tercero[ConfigFE.tercero_tipo_documento.name])
    #             if invoice.partner_id.fe_facturador
    #             else self._tipo_de_documento(self.parent_fe_tercero[ConfigFE.padre_tercero_tipo_documento.name]),
    #         'invoice_customer_identification': self.fe_tercero[ConfigFE.tercero_nit.name]
    #             if invoice.partner_id.fe_facturador
    #             else self.parent_fe_tercero[ConfigFE.padre_tercero_nit.name],
    #         'invoice_customer_identification_digit': self.fe_tercero[ConfigFE.tercero_digito_verificacion.name]
    #             if invoice.partner_id.fe_facturador
    #             else self.parent_fe_tercero[ConfigFE.padre_tercero_digito_verificacion.name],
    #         'invoice_customer_party_name': saxutils.escape(invoice.partner_id.name)
    #             if invoice.partner_id.fe_facturador
    #             else saxutils.escape(invoice.partner_id.parent_id.name),
    #         'invoice_customer_department': self.calcular_departamento(self.fe_tercero[ConfigFE.tercero_departamento.name])
    #             if invoice.partner_id.fe_facturador
    #             else self.calcular_departamento(self.parent_fe_tercero[ConfigFE.padre_tercero_departamento.name]),
    #         'invoice_customer_department_code': self.calcular_codigo_departamento(self.fe_tercero[ConfigFE.tercero_departamento.name])
    #             if invoice.partner_id.fe_facturador
    #             else self.calcular_codigo_departamento(self.parent_fe_tercero[ConfigFE.padre_tercero_departamento.name]),
    #         'invoice_customer_city': self.calcular_ciudad(self.fe_tercero[ConfigFE.tercero_ciudad.name])
    #             if invoice.partner_id.fe_facturador
    #             else self.calcular_ciudad(self.parent_fe_tercero[ConfigFE.padre_tercero_ciudad.name]),
    #         'invoice_customer_city_code': self.calcular_codigo_ciudad(self.fe_tercero[ConfigFE.tercero_ciudad.name])
    #             if invoice.partner_id.fe_facturador
    #             else self.calcular_codigo_ciudad(self.parent_fe_tercero[ConfigFE.padre_tercero_ciudad.name]),
    #         'invoice_customer_postal_code': (self.calcular_codigo_postal(self.fe_tercero[ConfigFE.tercero_postal.name]))
    #             if invoice.partner_id.fe_facturador
    #             else (self.calcular_codigo_postal(self.parent_fe_tercero[ConfigFE.padre_tercero_postal.name])),
    #         'invoice_customer_country': self.calcular_pais(self.fe_tercero[ConfigFE.tercero_pais.name])
    #             if invoice.partner_id.fe_facturador
    #             else self.calcular_pais(self.parent_fe_tercero[ConfigFE.padre_tercero_pais.name]),
    #         'invoice_customer_country_code': self.calcular_codigo_pais(self.fe_tercero[ConfigFE.tercero_pais.name])
    #             if invoice.partner_id.fe_facturador
    #             else self.calcular_codigo_pais(self.parent_fe_tercero[ConfigFE.padre_tercero_pais.name]),
    #         'invoice_customer_address_line': self.fe_tercero[ConfigFE.tercero_direccion.name]
    #             if invoice.partner_id.fe_facturador
    #             else self.parent_fe_tercero[ConfigFE.padre_tercero_direccion.name],
    #         'invoice_customer_tax_level_code':invoice_customer_tax_level_code,
    #         'invoice_customer_responsabilidad_tributaria':self.fe_tercero[ConfigFE.tercero_responsabilidad_tributaria.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_tributaria.name],
    #         'invoice_customer_responsabilidad_tributaria_text':self.calcular_texto_responsabilidad_tributaria(self.fe_tercero[ConfigFE.tercero_responsabilidad_tributaria.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_texto_responsabilidad_tributaria(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_tributaria.name]),
    #         'invoice_customer_first_name': invoice_customer_first_name,
    #         'invoice_customer_family_name': invoice_customer_family_name,
    #         'invoice_customer_family_last_name':invoice_customer_family_last_name,
    #         'invoice_customer_middle_name':invoice_customer_middle_name,
    #         'invoice_customer_phone': self.fe_tercero[ConfigFE.tercero_telefono.name]
    #             if invoice.partner_id.fe_facturador
    #             else self.parent_fe_tercero[ConfigFE.padre_tercero_telefono.name],
    #         'invoice_customer_commercial_registration':invoice_customer_commercial_registration,
    #         'invoice_customer_email': self.fe_tercero[ConfigFE.tercero_to_email.name]
    #             if invoice.partner_id.fe_facturador
    #             else self.parent_fe_tercero[ConfigFE.padre_tercero_to_email.name],
    #         # legal monetary total
    #         'line_extension_amount': '{:.2f}'.format(invoice.amount_untaxed),
    #         'tax_exclusive_amount': '{:.2f}'.format(tax_exclusive_amount),
    #         'tax_inclusive_amount': '{:.2f}'.format(invoice.amount_untaxed + total_impuestos),
    #         'payable_amount': '{:.2f}'.format(invoice.amount_total + invoice.total_withholding_amount),
    #         #'payable_amount': '{:.2f}'.format(invoice.amount_total + invoice.total_withholding_amount)
    #         #    if self.currency_id.name=='COP'
    #         #    else '{:.2f}'.format(invoice.amount_total + invoice.total_withholding_amount + invoice.invoice_charges_freight - invoice.invoice_discount),

    #         'payable_amount_discount': '{:.2f}'.format(invoice.amount_total + invoice.invoice_discount - invoice.invoice_charges_freight + invoice.total_withholding_amount)
    #             if self.currency_id.name == 'COP'
    #             else '{:.2f}'.format(invoice.amount_total + invoice.invoice_discount - invoice.invoice_charges_freight + invoice.total_withholding_amount),
    #         # invoice lines
    #         'creditnote_lines': creditnote_lines,
    #         'tax_total': tax_values,
    #         'tax_total_values': tax_total_values,
    #         'ret_total_values': ret_total_values,
    #         'date_due': invoice.invoice_date_due,
    #         # Info validaci??n previa
    #         'payment_means_id': self.forma_de_pago,
    #         'payment_means_code': self.payment_mean_id.codigo_fe_dian,
    #         'payment_id': self.payment_mean_id.nombre_tecnico_dian,
    #         'reference_event_code': self.invoice_payment_term_id.codigo_fe_dian,
    #         'duration_measure': duration_measure  if duration_measure else self.invoice_payment_term_id.line_ids.days,
    #         'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #         'order_reference': self.order_reference,
    #         'order_reference_date': self.order_reference_date,
    #         'additional_document_reference': self.additional_document_reference,
    #         'despatch_document_reference': self.despatch_document_reference,
    #         'despatch_document_reference_date': self.despatch_document_reference_date,
    #         'refacturapt_document_reference': self.refacturapt_document_reference,
    #         'refacturapt_document_reference_date': self.refacturapt_document_reference_date,

    #     }
    #     if invoice.amount_residual != invoice.amount_total:
    #         creditnote_fe_data.update({'prepaid_amount': invoice.amount_total - invoice.amount_residual,
    #                                 "invoice_prepaids": invoice_prepaids})
    #     #print("creditnote_fe_data:",creditnote_fe_data)

    #     #raise ValidationError("Para revisar")


    #     ##Validaci??n de C??digos Postales
    #     if invoice.partner_id.fe_facturador and not self.fe_tercero[ConfigFE.tercero_postal.name]:
    #         raise ValidationError("El cliente no tiene parametrizado C??digo Postal")
    #     if not invoice.partner_id.fe_facturador and not self.parent_fe_tercero[ConfigFE.padre_tercero_postal.name]:
    #         raise ValidationError("El padre del cliente no tiene parametrizado C??digo Postal")
    #     if not self.fe_company[ConfigFE.company_postal.name]:
    #         raise ValidationError("La Compa??ia no tiene parametrizado C??digo Postal")
    #     if self.fe_sucursal and not self.fe_sucursal_data[ConfigFE.sucursal_postal.name]:
    #         raise ValidationError("La sucursal no tiene parametrizado C??digo Postal")
    #     ##Fin de validaci??n

    #     if invoice.partner_id.fe_facturador:
    #         if self.fe_tercero[ConfigFE.tercero_es_compania.name] == '1':
    #             creditnote_fe_data['invoice_registration_name'] = saxutils.escape(self.fe_tercero[ConfigFE.tercero_razon_social.name])
    #         elif self.fe_tercero[ConfigFE.tercero_es_compania.name] == '2':
    #             creditnote_fe_data['invoice_customer_is_company'] = saxutils.escape(self.fe_tercero[ConfigFE.tercero_es_compania.name])
    #     else:
    #         if self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name] == '1':
    #             creditnote_fe_data['invoice_registration_name'] = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_razon_social.name])
    #         elif self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name] == '2':
    #             creditnote_fe_data['invoice_customer_is_company'] = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name])

    #     creditnote_fe_data['currency_id'] = self.currency_id.name
    #     creditnote_fe_data['calculation_rate'] = self.env.context['value_rate_exchange'] if 'value_check_rate' in self.env.context and self.env.context['value_check_rate'] else round(1 / self.currency_id.rate, 2)
    #     creditnote_fe_data['rate_date'] = self.date

    #     if self.es_nota_debito:
    #         creditnote_fe_data['discrepancy_response_code'] = self.concepto_correccion_debito
    #         creditnote_fe_data['billing_reference_id'] = self.credited_invoice_id.prefix_invoice_number()
    #         creditnote_fe_data['billing_reference_cufe'] = self.credited_invoice_id.cufe
    #         creditnote_fe_data['billing_reference_issue_date'] = self._str_to_datetime(self.create_date).strftime('%Y-%m-%d')
    #         xml_template = self.get_template_str('../templates/debitnote.xml')
    #         debit_note = Template(xml_template)
    #         output = debit_note.render(creditnote_fe_data)
    #     else:
    #         creditnote_fe_data['discrepancy_response_code'] = self.concepto_correccion_credito
    #         if self.reversed_entry_id.prefix_invoice_number():
    #             creditnote_fe_data['billing_reference_id'] = self.reversed_entry_id.prefix_invoice_number()
    #             creditnote_fe_data['billing_reference_cufe'] = self.reversed_entry_id.cufe
    #             creditnote_fe_data['billing_reference_issue_date'] = self._str_to_datetime(self.reversed_entry_id.create_date).strftime('%Y-%m-%d') if self.reversed_entry_id else ''
    #         else:
    #             creditnote_fe_data['billing_reference_id'] = self.numero_factura_origen
    #             creditnote_fe_data['billing_reference_cufe'] = self.cufe_factura_origen
    #             creditnote_fe_data['billing_reference_issue_date']=self.fecha_factura_origen

    #         xml_template = self.get_template_str('../templates/creditnote.xml')
    #         credit_note = Template(xml_template)
    #         output = credit_note.render(creditnote_fe_data)

    #     return output

    # # endregion
    # # region firmar_factura_electronica
    # def firmar_factura_electronica(self, event=False, filename="", event_name=""):
    #     invoice = self
    #     if not invoice.file and not event:
    #         raise ValidationError("El archivo no ha sido generado.")

    #     if invoice.firmado and not event:
    #         raise ValidationError("El archivo ya fue firmado.")

    #     if (invoice.type == 'out_invoice' and not event and
    #             not invoice.company_resolucion_id.tipo == 'facturacion-electronica'):
    #         raise ValidationError(
    #             "La resoluci??n debe ser de tipo 'facturaci??n electr??nica'"
    #         )

    #     _logger.info('Factura {} firmada correctamente'.format(invoice.name))
    #     # validar que campos para firma existan

    #     config = {
    #         'policy_id': self.company_id.fe_url_politica_firma,
    #         'policy_name': self.company_id.fe_descripcion_polica_firma,
    #         'policy_remote': self.company_id.fe_archivo_polica_firma,
    #         'key_file': self.company_id.fe_certificado,
    #         'key_file_password': self.company_id.fe_certificado_password,
    #     }
    #     if not event:
    #         firmado = sign(invoice.file, config)
    #     else:
    #         firmado = sign(invoice[event_name], config)

    #     # Asigna consecutivo de env??o y nombre definitivo para la factura.
    #     if not invoice.consecutivo_envio and not event:
    #         if invoice.type == 'out_invoice':
    #             invoice.consecutivo_envio = self.company_resolucion_id.proximo_consecutivo()
    #         elif invoice.type == 'out_refund':
    #             if self.company_resolucion_id.journal_id.refund_sequence_id:
    #                 invoice.consecutivo_envio = self.company_resolucion_id.proximo_consecutivo()
    #             else:
    #                 invoice.consecutivo_envio = self.company_resolucion_id.proximo_consecutivo()
    #         else:
    #             invoice.consecutivo_envio = invoice.id

    #     if not invoice.filename and not event:
    #         invoice.filename = self._get_fe_filename()

    #     buff = BytesIO()
    #     zip_file = zipfile.ZipFile(buff, mode='w')

    #     zip_content = BytesIO()
    #     zip_content.write(firmado)
    #     if event:
    #         zip_file.writestr(filename + '.xml', zip_content.getvalue())
    #     else:
    #         zip_file.writestr(invoice.filename + '.xml', zip_content.getvalue())

    #     zip_file.close()

    #     zipped_file = base64.b64encode(buff.getvalue())
    #     if event:
    #         invoice.sudo().write({
    #             event_name: zipped_file
    #         })
    #     else:
    #         invoice.sudo().write({
    #             'file': base64.b64encode(firmado),
    #             'firmado': True,
    #             'zipped_file': zipped_file
    #         })
    #     buff.close()

    # # endregion
    # # region _borrar_info_factura_electronica
    # def _borrar_info_factura_electronica(self):
    #     self.write({
    #         'filename': None,
    #         'firmado': False,
    #         'file': None,
    #         'zipped_file': None,
    #         'nonce': None,
    #         'qr_code': None,
    #         'cufe': None,
    #         'enviada': False,
    #         'enviada_error': False,
    #         'envio_fe_id': None,
    #     })

    # # endregion
    # # region borrar_factura_electronica

    # def borrar_factura_electronica(self):
    #     invoice = self
    #     if invoice.state != 'draft':
    #         raise ValidationError(
    #             "La factura debe encontrarse como "
    #             "borrador para poder realizar este proceso."
    #         )
    #     invoice._borrar_info_factura_electronica()

    # # endregion
    # # region copy

    # def copy(self):
    #     copied_invoice = super(Invoice, self).copy()
    #     copied_invoice._borrar_info_factura_electronica()
    #     return copied_invoice

    # # endregion
    # #region comment
    # # def enviar_factura_electronica(self):
    # #     if self.type == 'out_invoice' and not self.company_resolucion_id.tipo == 'facturacion-electronica':
    # #         raise ValidationError("La resoluci??n debe ser de tipo 'facturaci??n electronica'")
    # #
    # #     if self.enviada:
    # #         raise ValidationError('La factura electr??nica ya fue enviada a la DIAN.')
    # #
    # #     if not self.zipped_file:
    # #         raise ValidationError('No se encontr?? la factura electr??nica firmada')
    # #
    # #     response_nsd = {
    # #         'b': 'http://schemas.datacontract.org/2004/07/UploadDocumentResponse',
    # #         'c': 'http://schemas.datacontract.org/2004/07/XmlParamsResponseTrackId'
    # #     }
    # #     dian_webservice_url = self.env['ir.config_parameter'].search(
    # #         [('key', '=', 'dian.webservice.url')], limit=1).value
    # #
    # #     service = WsdlQueryHelper(
    # #         url=dian_webservice_url,
    # #         template_file=self.get_template_str('../templates/soap_skel.xml'),
    # #         key_file=self.company_id.fe_certificado,
    # #         passphrase=self.company_id.fe_certificado_password
    # #     )
    # #
    # #     _logger.info('Enviando factura {} al Webservice DIAN'.format(self.prefix_invoice_number()))
    # #
    # #     if self.company_id.fe_tipo_ambiente == '1':
    # #         response = service.send_bill_async(
    # #             zip_name=self.filename,
    # #             zip_data=self.zipped_file
    # #         )
    # #     elif self.company_id.fe_tipo_ambiente == '2':
    # #         response = service.send_test_set_async(
    # #             zip_name=self.filename,
    # #             zip_data=self.zipped_file,
    # #             test_set_id=self.company_id.fe_test_set_id
    # #         )
    # #     else:
    # #         raise ValidationError('Por favor configure el ambiente de destino en el men?? de su compa????a.')
    # #
    # #     if service.get_response_status_code() == 200:
    # #         xml_content = etree.fromstring(response)
    # #         track_id = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}ZipKey']
    # #         document_key = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}DocumentKey']
    # #         processed_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}ProcessedMessage']
    # #
    # #         if track_id and track_id[0].text is not None:
    # #             respuesta_envio = track_id[0].text
    # #         elif document_key and document_key[0].text is not None:
    # #             respuesta_envio = document_key[0].text
    # #         else:
    # #             respuesta_envio = processed_message[0].text if processed_message else 'Error en el env??o'
    # #
    # #         envio_fe = self.env['l10n_co_factura.envio_fe'].create({
    # #             'invoice_id': self.id,
    # #             'fecha_envio': datetime.datetime.now().astimezone(pytz.timezone('America/Bogota')),
    # #             'codigo_respuesta_envio': service.get_response_status_code(),
    # #             'respuesta_envio': respuesta_envio,
    # #             'nombre_archivo_envio': 'envio_{}_{}.xml'.format(
    # #                 self.number,
    # #                 datetime.datetime.now(pytz.timezone("America/Bogota")).strftime('%Y%m%d_%H%M%S')
    # #             ),
    # #             'archivo_envio': base64.b64encode(response.encode()),
    # #         })
    # #
    # #         if track_id:
    # #             if track_id[0].text is not None:
    # #                 envio_fe.write({
    # #                     'track_id': track_id[0].text
    # #                 })
    # #             else:
    # #                 envio_fe.write({
    # #                     'track_id': document_key[0].text
    # #                 })
    # #
    # #         self.write({
    # #             'envio_fe_id': envio_fe.id,
    # #             'enviada': True
    # #         })
    # #
    # #     else:
    # #         raise ValidationError(response)
    # # endregion
    # # region generar_attachment_xml
    # def generar_attachment_xml(self):
    #     try:
    #         response_nsd = {
    #             'b': 'http://schemas.datacontract.org/2004/07/DianResponse',
    #         }

    #         self.fe_company, self.fe_tercero, self.fe_sucursal_data, self.parent_fe_tercero = self._load_config_data()
    #         invoice = self
    #         if not self.fecha_xml:
    #             self.fecha_xml = datetime.datetime.combine(self.invoice_date, datetime.datetime.now().time())
    #         create_date = self._str_to_datetime(self.fecha_xml)
    #         deliver_date = self._str_to_datetime(self.fecha_entrega)

    #         key_data = '{}{}{}'.format(
    #             invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin,
    #             invoice.prefix_invoice_number()
    #         )
    #         sha384 = hashlib.sha384()
    #         sha384.update(key_data.encode())
    #         software_security_code = sha384.hexdigest()

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_primer_nombre.name]:
    #             invoice_customer_first_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_primer_nombre.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_primer_nombre.name]:
    #             invoice_customer_first_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_primer_nombre.name])
    #         else:
    #             invoice_customer_first_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_primer_apellido.name]:
    #             invoice_customer_family_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_primer_apellido.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_primer_apellido.name]:
    #             invoice_customer_family_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_primer_apellido.name])
    #         else:
    #             invoice_customer_family_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_segundo_apellido.name]:
    #             invoice_customer_family_last_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_segundo_apellido.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_apellido.name]:
    #             invoice_customer_family_last_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_apellido.name])
    #         else:
    #             invoice_customer_family_last_name = ''

    #         if invoice.partner_id.fe_facturador and self.fe_tercero[ConfigFE.tercero_segundo_nombre.name]:
    #             invoice_customer_middle_name = saxutils.escape(self.fe_tercero[ConfigFE.tercero_segundo_nombre.name])
    #         elif not invoice.partner_id.fe_facturador and self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_nombre.name]:
    #             invoice_customer_middle_name = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_segundo_nombre.name])
    #         else:
    #             invoice_customer_middle_name = ''

    #         if invoice.partner_id.fe_facturador:
    #             if type(self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name]).__name__ != 'list':
    #                 invoice_customer_tax_level_code = self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name]
    #             else:
    #                 invoice_customer_tax_level_code = ";".join(self.fe_tercero[ConfigFE.tercero_responsabilidad_fiscal.name])
    #         elif not invoice.partner_id.fe_facturador:
    #             if type(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name]).__name__ != 'list':
    #                 invoice_customer_tax_level_code = self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name]
    #             else:
    #                 invoice_customer_tax_level_code = ";".join(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_fiscal.name])



    #         invoice_fe_data = {
    #             'invoice_number': self.prefix_invoice_number(),
    #             'invoice_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'invoice_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_delivery_date': deliver_date.astimezone(pytz.timezone('America/Bogota')).strftime('%Y-%m-%d'),
    #             'invoice_delivery_time': deliver_date.astimezone(pytz.timezone('America/Bogota')).strftime('%H:%M:%S'),
    #             # supplier
    #             'invoice_supplier_document_type': self._tipo_de_documento(
    #                 self.fe_company[ConfigFE.company_tipo_documento.name]),
    #             'invoice_supplier_identification': self.fe_company[ConfigFE.company_nit.name],
    #             'invoice_supplier_identification_digit': self.fe_company[ConfigFE.company_digito_verificacion.name],
    #             'invoice_supplier_party_name': saxutils.escape(invoice.company_id.name),
    #             # customer
    #             'invoice_customer_document_type': self._tipo_de_documento(self.fe_tercero[ConfigFE.tercero_tipo_documento.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self._tipo_de_documento(self.parent_fe_tercero[ConfigFE.padre_tercero_tipo_documento.name]),
    #             'invoice_customer_identification': self.fe_tercero[ConfigFE.tercero_nit.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_nit.name],
    #             'invoice_customer_identification_digit': self.fe_tercero[ConfigFE.tercero_digito_verificacion.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_digito_verificacion.name],
    #             'invoice_customer_first_name': invoice_customer_first_name,
    #             'invoice_customer_family_name': invoice_customer_family_name,
    #             'invoice_customer_family_last_name':invoice_customer_family_last_name,
    #             'invoice_customer_middle_name':invoice_customer_middle_name,
    #             'invoice_customer_tax_level_code':invoice_customer_tax_level_code,
    #             'invoice_customer_responsabilidad_tributaria':self.fe_tercero[ConfigFE.tercero_responsabilidad_tributaria.name]
    #                 if invoice.partner_id.fe_facturador
    #                 else self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_tributaria.name],
    #             'invoice_customer_responsabilidad_tributaria_text':self.calcular_texto_responsabilidad_tributaria(self.fe_tercero[ConfigFE.tercero_responsabilidad_tributaria.name])
    #                 if invoice.partner_id.fe_facturador
    #                 else self.calcular_texto_responsabilidad_tributaria(self.parent_fe_tercero[ConfigFE.padre_tercero_responsabilidad_tributaria.name]),
    #         }

    #         if invoice.partner_id.fe_facturador:
    #             if self.fe_tercero[ConfigFE.tercero_es_compania.name] == '1':
    #                 invoice_fe_data['invoice_registration_name'] = saxutils.escape(self.fe_tercero[ConfigFE.tercero_razon_social.name])
    #             elif self.fe_tercero[ConfigFE.tercero_es_compania.name] == '2':
    #                 invoice_fe_data['invoice_customer_is_company'] = saxutils.escape(self.fe_tercero[ConfigFE.tercero_es_compania.name])
    #         else:
    #             if self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name] == '1':
    #                 invoice_fe_data['invoice_registration_name'] = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_razon_social.name])
    #             elif self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name] == '2':
    #                 invoice_fe_data['invoice_customer_is_company'] = saxutils.escape(self.parent_fe_tercero[ConfigFE.padre_tercero_es_compania.name])

    #         invoice_fe_data['envio_fecha_envio'] = self.envio_fe_id.fecha_envio.date()

    #         if self.envio_fe_id.codigo_respuesta_validacion == '00':
    #             codigo_respuesta_validacion_attached = '02'
    #         else:
    #             codigo_respuesta_validacion_attached = '04'
    #         invoice_fe_data['envio_codigo_respuesta_validacion'] = codigo_respuesta_validacion_attached
    #         invoice_fe_data['envio_fecha_validacion'] = self.envio_fe_id.fecha_validacion.strftime('%Y-%m-%d')
    #         invoice_fe_data['envio_hora_validacion'] = self.envio_fe_id.fecha_validacion.strftime('%H:%M:%S')

    #         invoice_fe_data['invoice_archivo_factura'] = base64.b64decode(self.file).decode()

    #         invoice_fe_data['invoice_cude'] = self.cufe

    #         if self.envio_fe_id.codigo_respuesta_validacion == '00':
    #             invoice_fe_data['envio_archivo_validacion'] = base64.b64decode([item for item in etree.fromstring(base64.b64decode(self.envio_fe_id.archivo_validacion).decode()).iter() if item.tag == '{' + response_nsd['b'] + '}XmlBase64Bytes'][0].text).decode()
    #         else:
    #             invoice_fe_data['envio_archivo_validacion'] = base64.b64decode(self.envio_fe_id.archivo_validacion).decode()

    #         xml_template = self.get_template_str('../templates/attacheddocument.xml')
    #         attached_template = Template(xml_template)
    #         output = attached_template.render(invoice_fe_data)

    #         return output
    #     except Exception as e:
    #         raise ValidationError(
    #             "Error validando la Attachment Document : {}".format(e)
    #         )

    # # endregion
    # # region enviar_factura_electronica
    # def enviar_factura_electronica(self):
    #     if self.type == 'out_invoice' and not self.company_resolucion_id.tipo == 'facturacion-electronica':
    #         raise ValidationError("La resoluci??n debe ser de tipo 'facturaci??n electr??nica'")

    #     if self.enviada:
    #         raise ValidationError('La factura electr??nica ya fue enviada a la DIAN.')

    #     if not self.zipped_file:
    #         raise ValidationError('No se encontr?? la factura electr??nica firmada')

    #     response_nsd = {
    #         'b': 'http://schemas.datacontract.org/2004/07/DianResponse',
    #         'c': 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
    #     }

    #     if self.company_id.fe_tipo_ambiente == '1':  # Producci??n
    #         dian_webservice_url = self.env['ir.config_parameter'].sudo().search(
    #             [('key', '=', 'dian.webservice.url')], limit=1).value
    #     else:
    #         dian_webservice_url = self.env['ir.config_parameter'].sudo().search(
    #             [('key', '=', 'dian.webservice.url.pruebas')], limit=1).value

    #     service = WsdlQueryHelper(
    #         url=dian_webservice_url,
    #         template_file=self.get_template_str('../templates/soap_skel.xml'),
    #         key_file=self.company_id.fe_certificado,
    #         passphrase=self.company_id.fe_certificado_password
    #     )

    #     _logger.info('Enviando factura {} al Webservice DIAN'.format(self.prefix_invoice_number()))

    #     if self.company_id.fe_tipo_ambiente == '1':  # Producci??n
    #         response = service.send_bill_sync(
    #             zip_name=self.filename,
    #             zip_data=self.zipped_file
    #         )

    #     # El metodo test async guarda la informacion en la grafica, el metodo bill_sync solo hace el conteo en los documentos (el test async habilita el set de pruebas el bill sync es para hacer pruebas sin habilitar el set)

    #     elif self.company_id.fe_tipo_ambiente == '2':  # Pruebas
    #         response = service.send_test_set_async(
    #             zip_name=self.filename,
    #             zip_data=self.zipped_file,
    #             test_set_id=self.company_id.fe_test_set_id
    #         )

    #     elif self.company_id.fe_tipo_ambiente == '3':  # Pruebas sin habilitacion
    #         response = service.send_bill_sync(
    #             zip_name=self.filename,
    #             zip_data=self.zipped_file
    #         )

    #     else:
    #         raise ValidationError('Por favor configure el ambiente de destino en el men?? de su compa????a.')

    #     val = {
    #         'company_id': self.company_id.id,
    #         'actividad': 'Envio de Factura a la DIAN',
    #         'fecha_hora': self.create_date,
    #         'factura': self.id,
    #         'estado': self.state,
    #         'type': 'Factura Electronica' if self.type=='out_invoice' and not self.es_nota_debito else 'Nota Debito' if self.type=='out_invoice' and self.es_nota_debito else'Nota Credito',
    #         'estado_validacion': self.fe_approved
    #     }
    #     self.env['l10n_co_factura.history'].create(val)

    #     if service.get_response_status_code() == 200:
    #         xml_content = etree.fromstring(response)
    #         track_id = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}ZipKey']

    #         if self.company_id.fe_tipo_ambiente == '1':  # El m??todo s??ncrono genera el CUFE como seguimiento
    #             document_key = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}XmlDocumentKey']
    #         else:  # El m??todo as??ncrono genera el ZipKey como n??mero de seguimiento
    #             document_key = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}DocumentKey']

    #         processed_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}ProcessedMessage']

    #         if track_id and track_id[0].text is not None:
    #             respuesta_envio = track_id[0].text
    #         elif document_key and document_key[0].text is not None:
    #             respuesta_envio = document_key[0].text
    #         else:
    #             respuesta_envio = processed_message[0].text if processed_message else self.cufe

    #         envio_fe = self.env['l10n_co_factura.envio_fe'].sudo().create({
    #             'invoice_id': self.id,
    #             'fecha_envio': datetime.datetime.now(),
    #             'codigo_respuesta_envio': service.get_response_status_code(),
    #             'respuesta_envio': respuesta_envio,
    #             'nombre_archivo_envio': 'envio_{}_{}.xml'.format(
    #                 self.name,
    #                 datetime.datetime.now(pytz.timezone("America/Bogota")).strftime('%Y%m%d_%H%M%S')
    #             ),
    #             'archivo_envio': base64.b64encode(response.encode()),
    #         })

    #         if track_id:
    #             if track_id[0].text is not None:
    #                 envio_fe.write({
    #                     'track_id': track_id[0].text
    #                 })
    #             else:
    #                 envio_fe.write({
    #                     'track_id': document_key[0].text
    #                 })

    #         self.write({
    #             'envio_fe_id': envio_fe.id,
    #             'enviada': True,
    #             'fe_approved': 'sin-calificacion'
    #         })

    #         # Producci??n - El env??o y la validaci??n se realizan en un solo paso.
    #         if self.company_id.fe_tipo_ambiente == '1':

    #             status_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusMessage']
    #             status_description = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusDescription']
    #             status_text = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}ErrorMessage']
    #             status_code = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusCode']
    #             validation_status = status_description[0].text if status_message else 'Error'
    #             validation_error = status_text[0].text if status_message else 'Error'
    #             validation_code = status_code[0].text if status_message else 'Error'

    #             if status_message:
    #                 log_status = status_message[0].text if status_message[0].text else status_description[0].text
    #             else:
    #                 log_status = 'Error'

    #             _logger.info('Respuesta de validaci??n => {}'.format(log_status))

    #             envio_fe.write({
    #                 'codigo_respuesta_validacion': status_code[0].text,
    #                 'respuesta_validacion': status_description[0].text,
    #                 'fecha_validacion': datetime.datetime.now(),
    #                 'nombre_archivo_validacion': 'validacion_{}_{}.xml'.format(
    #                     self.name,
    #                     datetime.datetime.now(pytz.timezone("America/Bogota")).strftime('%Y%m%d_%H%M%S')
    #                 ),
    #                 'archivo_validacion': base64.b64encode(response.encode('utf-8'))
    #             })

    #             output = self.generar_attachment_xml()
    #             self.sudo().write({'attachment_file': base64.b64encode(output.encode())})
    #             _logger.info('Attachmen Document generado')

    #             template = self.env.ref('l10n_co_factura.account_invoices_fe')

    #             render_template = template.render_qweb_pdf([self.id])

    #             buff = BytesIO()
    #             zip_file = zipfile.ZipFile(buff, mode='w')

    #             zip_content = BytesIO()
    #             zip_content.write(base64.b64decode(self.attachment_file))
    #             zip_file.writestr(self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.xml', zip_content.getvalue())

    #             zip_content = BytesIO()
    #             zip_content.write(base64.b64decode(base64.b64encode(render_template[0])))
    #             zip_file.writestr(self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.pdf', zip_content.getvalue())

    #             zip_file.close()

    #             zipped_file = base64.b64encode(buff.getvalue())

    #             self.sudo().write({'zipped_file': zipped_file})

    #             buff.close()

    #             if not self.attachment_id:
    #                 attachment = self.env['ir.attachment'].sudo().create({
    #                     'name': self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.zip',
    #                     'res_model': 'account.move',
    #                     'res_id': self.id,
    #                     'store_fname': self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.zip',
    #                     'mimetype': 'zip',
    #                     'datas': zipped_file,
    #                     'type': 'binary',
    #                 })

    #                 self.sudo().write({'attachment_id': attachment.id})

    #             if validation_code == '00' and not self.enviada_por_correo:
    #                 _logger.info('Enviando factura {} por correo electr??nico.'.format(self.prefix_invoice_number()))
    #                 self.notificar_correo()
    #                 self.enviada_por_correo = True
    #                 val = {
    #                     'company_id': self.company_id.id,
    #                     'actividad': 'Envio de Factura al Cliente',
    #                     'fecha_hora': self.write_date,
    #                     'factura': self.id,
    #                     'estado': self.state,
    #                     'type': 'Factura Electronica' if self.type=='out_invoice' and not self.es_nota_debito else 'Nota Debito' if self.type=='out_invoice' and self.es_nota_debito else'Nota Credito',
    #                     'estado_validacion': self.fe_approved,
    #                     'estado_dian': self.envio_fe_id.respuesta_validacion
    #                 }
    #                 self.env['l10n_co_factura.history'].create(val)

    #             if validation_code != '00' and not self.enviada_error:
    #                 _logger.info('Error en factura {} descripcion enviada por correo electr??nico.'.format(self.prefix_invoice_number()))
    #                 self.notificar_correo_error(self.prefix_invoice_number(), validation_status)
    #                 self.enviada_error = True
    #                 val = {
    #                     'company_id': self.company_id.id,
    #                     'actividad': 'Envio de de error al responsable de factura',
    #                     'fecha_hora': self.write_date,
    #                     'factura': self.id,
    #                     'estado': self.state,
    #                     'type': 'Factura Electronica' if self.type == 'out_invoice' and not self.es_nota_debito else 'Nota Debito' if self.type == 'out_invoice' and self.es_nota_debito else 'Nota Credito',
    #                     'estado_validacion': self.fe_approved,
    #                     'estado_dian': self.envio_fe_id.respuesta_validacion
    #                 }
    #                 self.env['l10n_co_factura.history'].create(val)

    #     else:
    #         raise ValidationError(response)

    # # endregion
    # # region notificar_correo
    # def notificar_correo(self, event=False, filename="", event_name="", event_code="",number_doc="",number_doc_ref=""):
    #     if not self.zipped_file and not event:
    #         raise ValidationError(
    #             'No se encontr?? la factura electr??nica firmada.'
    #         )

    #     if not self.enviada and not event:
    #         raise ValidationError(
    #             'La factura electr??nica a??n no ha sido enviada a la DIAN.'
    #         )
    #     archivos_fe_ids = []
    #     if not event:
    #         template = self.env.ref(
    #             'l10n_co_factura.approve_invoice_fe_email_template'
    #         )
    #         archivos_fe = self.env['l10n_co_factura.fe_archivos_email'].sudo().search([('invoice_id', '=', self.id)])
    #         zip_file = self.attachment_id

    #         for datos in archivos_fe:
    #             attachment_archivos_fe = self.env['ir.attachment'].sudo().search([('res_field', '!=', None),
    #                 ('res_id', '=', datos.id), ('res_model', '=', 'l10n_co_factura.fe_archivos_email'),
    #             ], limit=1)
    #             attachment_archivos_fe.name = datos.nombre_archivo_envio

    #             if attachment_archivos_fe:
    #                 archivos_fe_ids.append(attachment_archivos_fe.id)

    #     else:
    #         template = self.env.ref(
    #             'l10n_co_factura.approve_event_email_template'
    #         )
    #         zip_file = self[event_name.replace("file","attachment_id")]

    #     if zip_file:
    #         archivos_fe_ids.append(zip_file.id)

    #     if template:
    #         if event_code!="":
    #             template.subject = 'Evento;{};{};{};{};{}'.format(number_doc_ref,self.company_id.partner_id.fe_nit,self.company_id.name,number_doc,event_code)
    #         template.email_from = str(self.fe_company_email_from)
    #         template.attachment_ids = [(5, 0, [])]
    #         if archivos_fe_ids:
    #             template.attachment_ids = [(6, 0, archivos_fe_ids)]
    #         template.sudo().send_mail(self.id, force_send=True)
    #         template.attachment_ids = [(5, 0, [])]

    # # endregion
    # # region notificar_correo_error
    # def notificar_correo_error(self, name, error, event=False, filename="", event_name="", event_code="",number_doc="",number_doc_ref=""):
    #     if not self.zipped_file and not event:
    #         raise ValidationError(
    #             'No se encontr?? la factura electr??nica firmada.'
    #         )

    #     if not self.enviada and not event:
    #         raise ValidationError(
    #             'La factura electr??nica a??n no ha sido enviada a la DIAN.'
    #         )
    #     archivos_fe_ids = []

    #     if not event:
    #         template = self.env.ref(
    #             'l10n_co_factura.facturacion_template_validacion'
    #         )
    #         archivos_fe = self.env['l10n_co_factura.fe_archivos_email'].sudo().search([('invoice_id', '=', self.id)])

    #         zip_file = self.attachment_id

    #         for datos in archivos_fe:
    #             attachment_archivos_fe = self.env['ir.attachment'].sudo().search([('res_field', '!=', None),
    #             ('res_id', '=', datos.id),
    #             ('res_model', '=','l10n_co_factura.fe_archivos_email'), ],
    #             limit=1)
    #             attachment_archivos_fe.name = datos.nombre_archivo_envio

    #             if attachment_archivos_fe:
    #                 archivos_fe_ids.append(attachment_archivos_fe.id)

    #     else:
    #         template = self.env.ref(
    #             'l10n_co_factura.error_event_email_template'
    #         )
    #         zip_file = self[event_name.replace("file", "attachment_id")]

    #     archivos_fe_ids.append(zip_file.id)

    #     if template:
    #         template.email_from = str(self.fe_company_email_from)
    #         if event_code != "":
    #             template.subject = 'Fall??: Evento;{};{};{};{};{}'.format(number_doc_ref,self.company_id.partner_id.fe_nit,self.company_id.name,number_doc,event_code)
    #         error = error if error else 'Error en validaci??n de factura'
    #         template.body_html = error.replace('\n', '<br/>')
    #         template.email_to = self.env.company.fe_invoice_email
    #         template.attachment_ids = [(5, 0, [])]
    #         if archivos_fe_ids:
    #             template.attachment_ids = [(6, 0, archivos_fe_ids)]
    #         template.send_mail(self.id, force_send=True)
    #         template.attachment_ids = [(5, 0, [])]

    # # endregion
    # # region intento_envio_factura_electronica
    # def intento_envio_factura_electronica(self, event=False, filename="", event_name="",event_code="",number_doc="",number_doc_ref=""):
    #     for invoice in self:
    #         if invoice.fe_habilitar_facturacion_related:
    #             nsd = {
    #                 's': 'http://www.w3.org/2003/05/soap-envelope',
    #                 'u': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
    #             }
    #             # TODO: Mejorar o estandarizar este handling
    #             invoice._load_config_data()
    #             try:
    #                 if not event:
    #                     invoice.enviar_factura_electronica()
    #                 else:
    #                     respuesta,is_valid,validation_code = invoice.send_events(event, filename, event_name,event_code,number_doc,number_doc_ref)
    #             except Exception as e:
    #                 try:
    #                     msg, _ = e.args
    #                 except:
    #                     msg = e.args

    #                 try:
    #                     soap = etree.fromstring(msg)
    #                     msg_tag = [item for item in soap.iter() if item.tag == '{' + nsd['s'] + '}Text']
    #                     msg = msg_tag[0].text
    #                 except:
    #                     pass

    #                 _logger.error(
    #                     u'No fue posible enviar la factura electr??nica a la DIAN. Informaci??n del error: {}'.format(msg))
    #                 raise ValidationError(
    #                     u'No fue posible enviar la factura electr??nica a la DIAN.\n\nInformaci??n del error:\n\n {}'.format(msg))
    #             invoice._unload_config_data()
    #             if event:
    #                 return respuesta,is_valid, validation_code
    #         else:
    #             _logger.error(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')
    #             raise ValidationError(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')
    #         time.sleep(0.5)

    # def send_events(self, event=False, filename="", event_name="", event_code="",number_doc="",number_doc_ref=""):

    #     if event_name == 'file_send_acknowledgement_electronic_invoice' and not self.file_send_acknowledgement_electronic_invoice:
    #         raise ValidationError('No se encontr?? el evento de acuse de recibo')

    #     elif event_name == 'electronic_sales_invoice_claim' and not self.electronic_sales_invoice_claim:
    #         raise ValidationError('No se encontr?? el evento de reclamo de recibo de la factura de venta')

    #     elif event_name == 'refacturapt_services' and not self.refacturapt_services:
    #         raise ValidationError('No se encontr?? el evento de acuse de recibo de bien o prestaci??n de servicio')

    #     elif event_name == 'express_acceptance' and not self.express_acceptance:
    #         raise ValidationError('No se encontr?? el evento de aceptaci??n expresa')

    #     elif event_name == 'tacit_acceptance' and not self.tacit_acceptance:
    #         raise ValidationError('No se encontr?? el evento de aceptaci??n t??cita')

    #     response_nsd = {
    #         'b': 'http://schemas.datacontract.org/2004/07/DianResponse',
    #         'c': 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
    #     }

    #     if self.company_id.fe_tipo_ambiente == '1':  # Producci??n
    #         dian_webservice_url = self.env['ir.config_parameter'].sudo().search(
    #             [('key', '=', 'dian.webservice.url')], limit=1).value
    #     else:
    #         dian_webservice_url = self.env['ir.config_parameter'].sudo().search(
    #             [('key', '=', 'dian.webservice.url.pruebas')], limit=1).value

    #     service = WsdlQueryHelper(
    #         url=dian_webservice_url,
    #         template_file=self.get_template_str('../templates/soap_skel.xml'),
    #         key_file=self.company_id.fe_certificado,
    #         passphrase=self.company_id.fe_certificado_password
    #     )

    #     _logger.info('Enviando evento {} al Webservice DIAN'.format(event_name))

    #     if self.company_id.fe_tipo_ambiente == '1':  # Producci??n
    #         response = service.send_event_update_status(
    #             #zip_name=filename,
    #             zip_data=self[event_name]
    #         )

    #     # El metodo test async guarda la informacion en la grafica, el metodo bill_sync solo hace el conteo en los documentos (el test async habilita el set de pruebas el bill sync es para hacer pruebas sin habilitar el set)

    #     elif self.company_id.fe_tipo_ambiente == '2':  # Pruebas
    #         response = service.send_event_update_status(
    #             #zip_name=filename,
    #             zip_data=self[event_name],
    #             #test_set_id=self.company_id.fe_test_set_id
    #         )

    #     elif self.company_id.fe_tipo_ambiente == '3':  # Pruebas sin habilitacion
    #         response = service.send_event_update_status(
    #             #zip_name=filename,
    #             zip_data=self[event_name]
    #         )

    #     else:
    #         raise ValidationError('Por favor configure el ambiente de destino en el men?? de su compa????a.')

    #     val = {
    #         'company_id': self.company_id.id,
    #         'actividad': 'Envio de '+event_name,
    #         'fecha_hora': self.create_date,
    #         'factura': self.id,
    #         'estado': self.state,
    #         'type': event_name,
    #     }
    #     self.env['l10n_co_factura.history'].create(val)

    #     if service.get_response_status_code() == 200:
    #         xml_content = etree.fromstring(response)

    #         if self.company_id.fe_tipo_ambiente == '1':  # El m??todo s??ncrono genera el CUFE como seguimiento
    #             document_key = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}XmlDocumentKey']
    #         else:  # El m??todo as??ncrono genera el ZipKey como n??mero de seguimiento
    #             document_key = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}DocumentKey']

    #         processed_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}ProcessedMessage']

    #         is_valid = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}IsValid']
    #         status_code = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusCode']
    #         status_description = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusDescription']
    #         status_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusMessage']
    #         errors = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['c'] + '}string']

    #         if document_key and document_key[0].text is not None:
    #             respuesta_envio = document_key[0].text
    #         else:
    #             respuesta_envio = processed_message[0].text if processed_message else self.cufe

    #         respuesta=f"Respuesta de evento {event_name}:\nIsValid: {is_valid[0].text}\nStatusCode: {status_code[0].text}\nStatusDescription: {status_description[0].text}\nStatusMessage: {status_message[0].text if status_message and status_message[0].text != None else ''}\nMensaje: {errors[0].text if errors else ''}"
    #         _logger.info('Respuesta de validaci??n evento=> {}'.format(respuesta))

    #         #self.message_post(body=respuesta)

    #         # Producci??n - El env??o y la validaci??n se realizan en un solo paso.
    #         if self.company_id.fe_tipo_ambiente in ('1','2','3'):

    #             status_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusMessage']
    #             status_description = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusDescription']
    #             status_text = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}ErrorMessage']
    #             status_code = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusCode']
    #             validation_status = status_description[0].text if status_message else 'Error'
    #             validation_error = status_text[0].text if status_message else 'Error'
    #             validation_code = status_code[0].text if status_message else 'Error'

    #         return respuesta,is_valid,validation_code
    #     else:
    #         raise ValidationError(response)

    # def event_send_email(self,event,validation_code="", validation_status="",filename="", event_name="", event_code="",number_doc="",number_doc_ref=""):
    #     buff = BytesIO()
    #     zip_file = zipfile.ZipFile(buff, mode='w')

    #     zip_content = BytesIO()
    #     zip_content.write(base64.b64decode(self[event_name]))
    #     zip_file.writestr(filename + '.xml', zip_content.getvalue())
    #     zip_file.close()

    #     zipped_file = base64.b64encode(buff.getvalue())
    #     buff.close()

    #     if not self[event_name.replace('file', 'attachment_id')]:
    #         attachment = self.env['ir.attachment'].sudo().create({
    #             'name': filename + '.zip',
    #             'res_model': 'account.move',
    #             'res_id': self.id,
    #             'store_fname': filename + '.zip',
    #             'mimetype': 'zip',
    #             'datas': zipped_file,
    #             'type': 'binary',
    #         })

    #         self[event_name.replace('file', 'attachment_id')] = attachment.id

    #     if validation_code == '00':
    #         _logger.info('Enviando evento {} por correo electr??nico.'.format(event_name))
    #         if event_name != "file_tacit_acceptance":
    #             self.notificar_correo(event, filename, event_name, event_code, number_doc, number_doc_ref)
    #             val = {
    #                 'company_id': self.company_id.id,
    #                 'actividad': 'Envio de evento ' + event_name,
    #                 'fecha_hora': self.write_date,
    #                 'factura': self.id,
    #                 'estado': self.state,
    #                 'type': event_name
    #             }
    #             self.env['l10n_co_factura.history'].create(val)

    #     if validation_code != '00' and not self.enviada_error:
    #         _logger.info('Error en evento{} descripcion enviada por correo electr??nico.'.format(event_name))

    #         self.notificar_correo_error(self.prefix_invoice_number(), validation_status, event, filename,
    #                                     event_name, event_code, number_doc, number_doc_ref)
    #         val = {
    #             'company_id': self.company_id.id,
    #             'actividad': 'Envio de de error al responsable de evento ' + event_name,
    #             'fecha_hora': self.write_date,
    #             'factura': self.id,
    #             'estado': self.state,
    #             'type': event_name
    #         }
    #         self.env['l10n_co_factura.history'].create(val)


    # # endregion
    # # region type_out_invoice
    # def type_out_invoice(self):
    #     try:
    #         if self.fe_habilitar_facturacion_related:
    #             resolucion = None
    #             self.es_factura_electronica = True

    #             if not self.partner_id.fe_habilitada:
    #                 raise ValidationError(
    #                     "Este usuario no se encuentra habilitado para Facturar Electronicamente \n\n"
    #                     "Habilite la Facturaci??n Electr??nica dentro del modulo de contactos"
    #                 )

    #             if not self.company_id.fe_software_id:
    #                 raise ValidationError(
    #                     "El ID de software de facturaci??n electr??nica no ha sido "
    #                     "configurado en registro de empresa (res.company.fe_software_id)"
    #                 )
    #             if not self.company_id.fe_software_pin:
    #                 raise ValidationError(
    #                     "El PIN de facturaci??n electr??nica no ha sido configurado en registro "
    #                     "de empresa (res.company.fe_software_pin)"
    #                 )

    #             if not self.name or self.name =='/':
    #                 resolucion = self.env['l10n_co_factura.company_resolucion'].sudo().search([
    #                     ('id', '=', self.journal_id.company_resolucion_factura_id.id),
    #                 ], limit=1)

    #                 if not resolucion:
    #                     raise ValidationError(
    #                         "No se encontr?? resoluci??n activa."
    #                     )
    #                 # check if number is within the range
    #                 if not resolucion.check_resolution():
    #                     raise ValidationError(
    #                         "Consecutivos de resoluci??n agotados."
    #                     )
    #                 if self.invoice_date:
    #                     if not resolucion.check_resolution_date(self.invoice_date):
    #                         raise ValidationError(
    #                             "La fecha del documento no se encuentra dentro del rango de la resoluci??n"
    #                         )
    #                 else:
    #                     today = date.today()
    #                     if not resolucion.check_resolution_date(today):
    #                         raise ValidationError(
    #                             "La fecha actual no se encuentra dentro del rango de la resoluci??n"
    #                         )
    #                 if not resolucion.category_resolution_dian_id:
    #                     raise ValidationError(
    #                         "Por favor configure la resoluci??n con la categoria asociada a la Dian"
    #                     )
    #                 #if self.type == 'out_invoice':
    #                  #   for line in self.invoice_line_ids:
    #                  #       if not line.product_uom_id.unit_measurement_id:
    #                    #         raise ValidationError(
    #                    #             "El producto (%s) no tiene configurado correctamente el tipo de unidad con el c??digo Dian" % line.name)


    #             for index, invoice_line_id in enumerate(self.invoice_line_ids):
    #                 taxes = invoice_line_id.tax_ids

    #                 for tax in taxes:
    #                     if not tax.codigo_fe_dian or not tax.nombre_tecnico_dian:
    #                         raise ValidationError(
    #                             'Por favor configure los campos c??digo y nombre DIAN '
    #                             'para el impuesto {}'.format(tax.name)
    #                         )

    #             msg = ""
    #             for index, invoice_line_id in enumerate(self.invoice_line_ids):
    #                 if invoice_line_id.display_type not in ['line_section','line_note'] and invoice_line_id.price_unit == 0 and invoice_line_id.line_price_reference == 0:
    #                     msg += "- Si el precio unitario es 0.00, el precio de referencia debe indicar el precio real, no puede ser 0.00.\n"
    #                 if invoice_line_id.price_unit == 0 and invoice_line_id.line_trade_sample == False:
    #                     msg += "- Si se tiene una l??nea en la cual el precio unitario es 0.00, se debe seleccionar el check de muestra comercial e indicar la referencia al precio real.\n"
    #                 if msg != "":
    #                     raise ValidationError(_(msg))
    #         self._load_config_data()
    #     except Exception as e:
    #         raise ValidationError(e)
    #     super(Invoice, self).post()
    #     #self._compute_payments_widget_to_reconcile_info()
    #     for prepaid_move_line in self.pre_payment_line_ids:
    #         #print("prepaid_move_line.id:",prepaid_move_line.id)
    #         self.js_assign_outstanding_line(prepaid_move_line.id)
    #     #print('Acabo la conciliacion............')
    #     try:
    #         if self.fe_habilitar_facturacion_related:
    #             if not self.company_resolucion_id and resolucion:
    #                 self.company_resolucion_id = resolucion.id

    #             self.access_token = self.access_token if self.access_token else str(uuid.uuid4())
    #             self.generar_factura_electronica()
    #             self.firmar_factura_electronica()

    #             self._unload_config_data()
    #     except Exception as e:
    #         raise ValidationError(e)

    # # endregion
    # # region type_out_refund
    # def type_out_refund(self):
    #     try:
    #         if self.fe_habilitar_facturacion_related:
    #             self.es_factura_electronica = True

    #             if not self.partner_id.fe_habilitada:
    #                 raise ValidationError(
    #                     "Este usuario no se encuentra habilitado para Facturar Electronicamente \n\n"
    #                     "Habilite la Facturaci??n Electr??nica dentro del modulo de contactos"
    #                 )

    #             if not self.company_id.fe_software_id:
    #                 raise ValidationError(
    #                     "El ID de facturaci??n electr??nica no ha sido configurado "
    #                     "en registro de empresa (res.company.fe_software_id)"
    #                 )
    #             if not self.company_id.fe_software_pin:
    #                 raise ValidationError(
    #                     "El PIN de facturaci??n electr??nica no ha sido configurado en registro "
    #                     "de empresa (res.company.fe_software_pin)"
    #                 )

    #             resolucion = self.env['l10n_co_factura.company_resolucion'].sudo().search([
    #                 ('id', '=', self.journal_id.company_resolucion_credito_id.id),
    #             ], limit=1)

    #             if not resolucion:
    #                 raise ValidationError(
    #                     "No se encontr?? resoluci??n activa."
    #                 )
    #             # check if number is within the range
    #             if not resolucion.check_resolution():
    #                 raise ValidationError(
    #                     "Consecutivos de resoluci??n agotados."
    #                 )
    #             if self.invoice_date:
    #                 if not resolucion.check_resolution_date(self.invoice_date):
    #                     raise ValidationError(
    #                         "La fecha del documento no se encuentra dentro del rango de la resoluci??n"
    #                     )
    #             else:
    #                 today = date.today()
    #                 if not resolucion.check_resolution_date(today):
    #                     raise ValidationError(
    #                         "La fecha actual no se encuentra dentro del rango de la resoluci??n"
    #                     )
    #             if not resolucion.category_resolution_dian_id:
    #                 raise ValidationError(
    #                     "Por favor configure la resoluci??n de la nota cr??dito con la categoria asociada a la Dian"
    #                 )

    #             for index, invoice_line_id in enumerate(self.invoice_line_ids):
    #                 taxes = invoice_line_id.tax_ids

    #                 for tax in taxes:
    #                     if not tax.codigo_fe_dian or not tax.nombre_tecnico_dian:
    #                         raise ValidationError(
    #                             'Por favor configure los campos c??digo y nombre DIAN '
    #                             'para el impuesto {}'.format(tax.name)
    #                         )
    #         self._load_config_data()
    #     except Exception as e:
    #         raise ValidationError(e)
    #     #super(Invoice, self).action_post()
    #     super(Invoice, self).post()

    #     try:
    #         if self.fe_habilitar_facturacion_related:
    #             if not self.company_resolucion_id and resolucion:
    #                 self.company_resolucion_id = resolucion.id

    #             self.access_token = self.access_token if self.access_token else str(uuid.uuid4())

    #             self.generar_factura_electronica()
    #             self.firmar_factura_electronica()

    #             self._unload_config_data()
    #     except Exception as e:
    #         raise ValidationError(e)

    # # endregion
    # # region post
    # # asigna consecutivo de facturacion electronica
    # #def action_post(self):
    # def post(self):
    #     for invoice in self:
    #         if invoice.type == 'out_invoice':
    #             if invoice.es_factura_exportacion and not invoice.es_nota_debito:
    #                 invoice.category_resolution_dian_id = invoice.journal_id.company_resolucion_factura_id.xp_category_resolution_dian_id.id
    #             else:
    #                 invoice.category_resolution_dian_id = invoice.journal_id.company_resolucion_factura_id.category_resolution_dian_id.id
    #         else:
    #             if invoice.journal_id.company_resolucion_credito_id:
    #                 invoice.category_resolution_dian_id = invoice.journal_id.company_resolucion_credito_id.category_resolution_dian_id.id
    #             else:
    #                 invoice.category_resolution_dian_id = invoice.journal_id.company_resolucion_factura_id.category_resolution_dian_id.id

    #         vector = self._load_config_data()
    #         invoice.fe_company = vector[0]
    #         invoice.fe_tercero = vector[1]
    #         invoice.fe_sucursal_data = vector[2]
    #         invoice.parent_fe_tercero = vector[3]

    #         resolucion = self.env['l10n_co_factura.company_resolucion'].sudo().search([
    #             ('company_id', '=', invoice.company_id.id),
    #             ('journal_id', '=', invoice.journal_id.id),
    #             ('state', '=', 'active'),
    #         ], limit=1)

    #         if invoice.type == 'out_invoice' and resolucion.tipo == 'facturacion-electronica':
    #             invoice.type_out_invoice()
    #         elif invoice.type == 'out_refund' and resolucion.tipo == 'facturacion-electronica':
    #             """if not self.reversed_entry_id:
    #                 raise ValidationError(
    #                     "No se pueden validar facturas cr??dito que no esten vinculadas "
    #                     "a una factura existente."
    #                 )
    #             else:"""
    #             invoice.type_out_refund()
    #         else:
    #             super(Invoice, invoice).post()
    #             #super(Invoice, self).action_post()
    #         #return self
    #         return True

    #     # Correcci??n de metodo action_post_create para sobrecargar parte del metodo principal

    # # endregion
    # # region download_xml
    # def download_xml(self):
    #     if self.fe_habilitar_facturacion_related:
    #         if self.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             # global fe_company
    #             config_fe = self._get_config()
    #             self.fe_company = {
    #                 ConfigFE.company_nit.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_nit.name,
    #                     obj_id=self.id
    #                 )
    #             }
    #             filename = self._get_fe_filename()
    #             self.fe_company = None

    #             return {
    #                 'name': 'Report',
    #                 'type': 'ir.actions.act_url',
    #                 'url': (
    #                         "web/content/?model=" +
    #                         self._name + "&id=" + str(self.id) +
    #                         "&filename_field=filename&field=file&download=true&filename=" +
    #                         filename + '.xml'
    #                 ),
    #                 'target': 'self',
    #             }
    #         else:
    #             _logger.error(u'Este documento no corresponde a una Factura Electr??nica')
    #             raise ValidationError(u'Este documento no corresponde a una Factura Electr??nica')
    #     else:
    #         _logger.error(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')
    #         raise ValidationError(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')

    # # endregion
    # # region download_xml_firmado
    # def download_xml_firmado(self):
    #     if self.fe_habilitar_facturacion_related:
    #         if self.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             filename = self._get_fe_filename()

    #             if filename:
    #                 return {
    #                     'name': 'Report',
    #                     'type': 'ir.actions.act_url',
    #                     'url': "web/content/?model=" + self._name + "&id=" + str(
    #                         self.id) + "&filename_field=filename&field=zipped_file&download=true&filename=" + filename + '.zip',
    #                     'target': 'self',
    #                 }
    #             else:
    #                 return {
    #                     'name': 'Report',
    #                     'type': 'ir.actions.act_url',
    #                     'url': "web/content/?model=" + self._name + "&id=" + str(
    #                         self.id) + "&filename_field=filename&field=zipped_file&download=true&filename=False.zip",
    #                     'target': 'self',
    #                 }
    #         else:
    #             _logger.error(u'Este documento no corresponde a una Factura Electr??nica')
    #             raise ValidationError(u'Este documento no corresponde a una Factura Electr??nica')
    #     else:
    #         _logger.error(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')
    #         raise ValidationError(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')

    # # endregion
    # # region download_xml_attachment
    # def download_xml_attachment(self):
    #     if self.fe_habilitar_facturacion_related:
    #         if self.tipo_resolucion_diario_f == 'facturacion-electronica':
    #             config_fe = self._get_config()
    #             self.fe_company = {
    #                 ConfigFE.company_nit.name: config_fe.get_value(
    #                     field_name=ConfigFE.company_nit.name,
    #                     obj_id=self.id
    #                 )
    #             }
    #             filename = self._get_fe_filename()
    #             self.fe_company = None

    #             if 'fv' in filename:
    #                 filename = filename.replace('fv', 'ad')
    #             if 'nc' in filename:
    #                 filename = filename.replace('nc', 'ad')
    #             if 'nd' in filename:
    #                 filename = filename.replace('nd', 'ad')

    #             return {
    #                 'name': 'Report',
    #                 'type': 'ir.actions.act_url',
    #                 'url': (
    #                         "web/content/?model=" +
    #                         self._name + "&id=" + str(self.id) +
    #                         "&filename_field=filename&field=attachment_file&download=true&filename=" +
    #                         filename + '.xml'
    #                 ),
    #                 'target': 'self',
    #             }
    #         else:
    #             _logger.error(u'Este documento no corresponde a una Factura Electr??nica')
    #             raise ValidationError(u'Este documento no corresponde a una Factura Electr??nica')
    #     else:
    #         _logger.error(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')
    #         raise ValidationError(u'Esta compa??ia no tiene habilitada Facturaci??n Electr??nica para Colombia')

    # def send_acknowledgement_electronic_invoice(self):
    #     if self.file_send_acknowledgement_electronic_invoice:
    #         raise ValidationError("No se puede generar el evento acuse de recibo, porque ya se gener?? anteriormente")

    #     user_id = self.env.user
    #     create_date = datetime.datetime.now()

    #     if not self.ref or not self.supplier_invoice_cufe or not self.supplier_invoice_type or not user_id.partner_id.fe_nit \
    #             or not user_id.partner_id.fe_digito_verificacion or not user_id.partner_id.fe_tipo_documento \
    #             or not user_id.partner_id.fe_es_compania or not self.company_id.partner_id.fe_nit \
    #             or not self.company_id.partner_id.fe_digito_verificacion or not self.company_id.partner_id.fe_tipo_documento \
    #             or not self.company_id.partner_id.fe_es_compania or not self.partner_id.fe_nit \
    #             or not self.partner_id.fe_digito_verificacion or not self.partner_id.fe_tipo_documento or \
    #             not self.partner_id.fe_es_compania or not self.journal_id.send_acknowledgement_electronic_invoice_sequence_id:
    #         raise ValidationError(
    #             "Revisar que los siguientes campos no esten vacios: Referencia, CUFE Factura Proveedor, Tipo factura proveedor, "
    #             "Sequencia ApplicationResponse Acuse Recibo en Diario, Tipo de documento/Nit/Digito Verificacion/"
    #             "Tipo persona en Cliente, Tipo de documento/Nit/Digito Verificacion/Tipo persona en Compa??ia, "
    #             "Tipo de documento/Nit/Digito Verificacion/Tipo persona en Usuario")

    #     nit = str(self.company_id.partner_id.fe_nit).zfill(10)
    #     current_year = datetime.datetime.now().replace(tzinfo=pytz.timezone('America/Bogota')).strftime('%Y')

    #     prefix = self.journal_id.send_acknowledgement_electronic_invoice_sequence_id.prefix
    #     consecutivo = self.journal_id.send_acknowledgement_electronic_invoice_sequence_id._next_do().replace(prefix,"")

    #     filename = 'ar{}000{}{}'.format(nit, current_year[-2:], str(hex(int(consecutivo))).split("x")[1].zfill(8))

    #     invoice = self
    #     key_data = '{}{}{}'.format(
    #         invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin,
    #         prefix+str(consecutivo)
    #     )
    #     sha384 = hashlib.sha384()
    #     sha384.update(key_data.encode())
    #     software_security_code = sha384.hexdigest()


    #     try:
    #         invoice_fe_data = {
    #             'fe_nit': invoice.company_id.partner_id.fe_nit,
    #             'fe_digito_verificacion': invoice.company_id.partner_id.fe_digito_verificacion,
    #             'fe_software_id': invoice.company_id.fe_software_id,
    #             'software_security_code': software_security_code,
    #             'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'de_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'de_issue_time':  create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_customer_party_name': saxutils.escape(invoice.company_id.name),
    #             'invoice_customer_identification': self.company_id.partner_id.fe_nit,
    #             'invoice_customer_identification_digit': self.company_id.partner_id.fe_digito_verificacion,
    #             'invoice_customer_responsabilidad_tributaria': self.company_id.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_customer_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.company_id.partner_id.fe_responsabilidad_tributaria),
    #             'invoice_customer_type_person': self.company_id.partner_id.fe_es_compania,
    #             'invoice_customer_document_type': self.company_id.partner_id.fe_tipo_documento,
    #             'invoice_supplier_type_person': self.partner_id.fe_es_compania,
    #             'invoice_supplier_party_name': saxutils.escape(invoice.partner_id.name) if invoice.partner_id.fe_facturador else saxutils.escape(invoice.partner_id.parent_id.name),
    #             'invoice_supplier_identification': self.partner_id.fe_nit,
    #             'invoice_supplier_identification_digit': self.partner_id.fe_digito_verificacion,
    #             'invoice_supplier_document_type': self.partner_id.fe_tipo_documento,
    #             'invoice_supplier_responsabilidad_tributaria': self.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_supplier_responsabilidad_tributaria_text':self.calcular_texto_responsabilidad_tributaria(self.partner_id.fe_responsabilidad_tributaria),
    #             'refacturaver_id': user_id.partner_id.fe_nit,
    #             'refacturaver_document_type': user_id.partner_id.fe_tipo_documento,
    #             'refacturaver_verification_digit': user_id.partner_id.fe_digito_verificacion,
    #             'refacturaver_first_name': user_id.partner_id.fe_primer_nombre + user_id.partner_id.fe_segundo_nombre if user_id.partner_id.fe_segundo_nombre else user_id.partner_id.fe_primer_nombre,
    #             'refacturaver_second_name': user_id.partner_id.fe_primer_apellido + user_id.partner_id.fe_segundo_apellido if user_id.partner_id.fe_segundo_apellido else user_id.partner_id.fe_primer_apellido,
    #             'application_response_id': prefix+str(consecutivo),
    #             'document_reference': self.ref,
    #             'de_cude': self.generate_cude("030",create_date, prefix+str(consecutivo)),
    #             'profile_execution_cude_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'invoice_cufe': self.supplier_invoice_cufe,
    #             'document_type_reference': self.supplier_invoice_type,
    #         }
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al formar el diccionario de datos {}".format(e))

    #     try:
    #         xml_template = self.get_template_str('../templates/acuse_recibo_fev.xml')
    #         export_template = Template(xml_template)
    #         output = export_template.render(invoice_fe_data)
    #         event_name = 'file_send_acknowledgement_electronic_invoice'
    #         invoice.sudo().write({
    #             event_name: base64.b64encode(output.encode())
    #         })
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al renderizar la plantilla {}".format(e))
    #     try:
    #         self.firmar_factura_electronica(True, filename, event_name)
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en la firma del documento {}".format(e))

    #     try:
    #         self.filename_send_acknowledgement_electronic_invoice = prefix+str(consecutivo)
    #         respuesta, is_valid, validation_code = self.intento_envio_factura_electronica(True, filename,event_name,'030',prefix+str(consecutivo),self.ref)
    #         self[event_name.replace('file','answer')] = respuesta
    #         self.env.cr.commit()
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en el envio del documento a la DIAN {}".format(e))

    #     try:
    #         self.event_send_email(True, validation_code,respuesta,filename, event_name, '030', prefix + str(consecutivo),self.ref)
    #         self.email_send_acknowledgement_electronic_invoice = True
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error en el envio del documento al proveedor {}".format(e))

    # def electronic_sales_invoice_claim(self):
    #     if not self.file_send_acknowledgement_electronic_invoice:
    #         raise ValidationError("No se puede generar el evento de reclamo de la factura de venta, porque no se ha generado el acuse de recibo")
    #     if not self.file_refacturapt_services:
    #         raise ValidationError("No se puede generar el evento de reclamo de la factura de venta, porque no se ha generado el acuse de recibo de bienes o servicios")
    #     if self.file_electronic_sales_invoice_claim:
    #         raise ValidationError("No se puede generar el evento de reclamo de la factura de venta, porque ya se gener?? anteriormente")
    #     if self.file_express_acceptance:
    #         raise ValidationError("No se puede generar el evento de reclamo de la factura de venta, porque ya se acept?? anteriormente")

    #     user_id = self.env.user
    #     create_date = datetime.datetime.now()

    #     if not self.supplier_invoice_cufe or not self.supplier_invoice_type or not user_id.partner_id.fe_nit \
    #             or not user_id.partner_id.fe_digito_verificacion or not user_id.partner_id.fe_tipo_documento \
    #             or not user_id.partner_id.fe_es_compania or not self.company_id.partner_id.fe_nit \
    #             or not self.company_id.partner_id.fe_digito_verificacion or not self.company_id.partner_id.fe_tipo_documento \
    #             or not self.company_id.partner_id.fe_es_compania or not self.partner_id.fe_nit \
    #             or not self.partner_id.fe_digito_verificacion or not self.partner_id.fe_tipo_documento or \
    #             not self.partner_id.fe_es_compania or not self.journal_id.electronic_sales_invoice_claim_sequence_id or not self.supplier_claim_concept:
    #         raise ValidationError(
    #             "Revisar que los siguientes campos no esten vacios: CUFE Factura Proveedor, Tipo factura proveedor, "
    #             "Sequencia ApplicationResponse Acuse Recibo en Diario, Tipo de documento/Nit/Digito Verificacion/"
    #             "Tipo persona en Cliente, Tipo de documento/Nit/Digito Verificacion/Tipo persona en Compa??ia, "
    #             "Tipo de documento/Nit/Digito Verificacion/Tipo persona en Usuario, "
    #             "Concepto de reclamo")

    #     nit = str(self.partner_id.fe_nit).zfill(10)
    #     current_year = datetime.datetime.now().replace(tzinfo=pytz.timezone('America/Bogota')).strftime('%Y')

    #     prefix = self.journal_id.electronic_sales_invoice_claim_sequence_id.prefix
    #     consecutivo = int(self.journal_id.electronic_sales_invoice_claim_sequence_id._next_do().replace(prefix, ""))

    #     filename = 'ar{}000{}{}'.format(nit, current_year[-2:], str(hex(int(consecutivo))).split("x")[1].zfill(8))

    #     invoice = self
    #     key_data = '{}{}{}'.format(
    #         invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin,
    #         prefix + str(consecutivo)
    #     )
    #     sha384 = hashlib.sha384()
    #     sha384.update(key_data.encode())
    #     software_security_code = sha384.hexdigest()


    #     try:
    #         invoice_fe_data = {
    #             'fe_nit': invoice.company_id.partner_id.fe_nit,
    #             'fe_digito_verificacion': invoice.company_id.partner_id.fe_digito_verificacion,
    #             'fe_software_id': invoice.company_id.fe_software_id,
    #             'software_security_code': software_security_code,
    #             'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'de_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'de_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_customer_party_name': saxutils.escape(invoice.company_id.name),
    #             'invoice_customer_identification': self.company_id.partner_id.fe_nit,
    #             'invoice_customer_identification_digit': self.company_id.partner_id.fe_digito_verificacion,
    #             'invoice_customer_responsabilidad_tributaria': self.company_id.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_customer_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.company_id.partner_id.fe_responsabilidad_tributaria),
    #             'invoice_customer_type_person': self.company_id.partner_id.fe_es_compania,
    #             'invoice_customer_document_type': self.company_id.partner_id.fe_tipo_documento,
    #             'invoice_supplier_type_person': self.partner_id.fe_es_compania,
    #             'invoice_supplier_party_name': saxutils.escape(invoice.partner_id.name) if invoice.partner_id.fe_facturador else saxutils.escape(invoice.partner_id.parent_id.name),
    #             'invoice_supplier_identification': self.partner_id.fe_nit,
    #             'invoice_supplier_identification_digit': self.partner_id.fe_digito_verificacion,
    #             'invoice_supplier_document_type': self.partner_id.fe_tipo_documento,
    #             'invoice_supplier_responsabilidad_tributaria': self.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_supplier_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.partner_id.fe_responsabilidad_tributaria),
    #             'refacturaver_id': user_id.partner_id.fe_nit,
    #             'refacturaver_document_type': user_id.partner_id.fe_tipo_documento,
    #             'refacturaver_verification_digit': user_id.partner_id.fe_digito_verificacion,
    #             'refacturaver_first_name': user_id.partner_id.fe_primer_nombre + user_id.partner_id.fe_segundo_nombre if user_id.partner_id.fe_segundo_nombre else user_id.partner_id.fe_primer_nombre,
    #             'refacturaver_second_name': user_id.partner_id.fe_primer_apellido + user_id.partner_id.fe_segundo_apellido if user_id.partner_id.fe_segundo_apellido else user_id.partner_id.fe_primer_apellido,
    #             'application_response_id': prefix + str(consecutivo),
    #             'document_reference': self.ref,
    #             'de_cude': self.generate_cude("031", create_date, prefix + str(consecutivo)),
    #             'profile_execution_cude_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'invoice_cufe': self.supplier_invoice_cufe,
    #             'document_type_reference': self.supplier_invoice_type,
    #             'supplier_claim_concept': self.supplier_claim_concept,
    #             'supplier_claim_concept_text': self.calculate_text_supplier_claim_concept(self.supplier_claim_concept),
    #         }
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al formar el diccionario de datos {}".format(e))

    #     try:
    #         xml_template = self.get_template_str('../templates/reclamo_fev.xml')
    #         export_template = Template(xml_template)
    #         output = export_template.render(invoice_fe_data)
    #         event_name = 'file_electronic_sales_invoice_claim'
    #         invoice.sudo().write({
    #             event_name: base64.b64encode(output.encode())
    #         })
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al renderizar la plantilla {}".format(e))
    #     try:
    #         self.firmar_factura_electronica(True, filename, event_name)
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en la firma del documento {}".format(e))

    #     try:
    #         self.filename_electronic_sales_invoice_claim = prefix+str(consecutivo)
    #         respuesta, is_valid, validation_code = self.intento_envio_factura_electronica(True, filename, event_name,'031',prefix+str(consecutivo),self.ref)
    #         self[event_name.replace('file', 'answer')] = respuesta
    #         self.env.cr.commit()
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en el envio del documento a la DIAN {}".format(e))

    #     try:
    #         self.event_send_email(True, validation_code,respuesta,filename, event_name, '031', prefix + str(consecutivo),self.ref)
    #         self.email_electronic_sales_invoice_claim = True
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error en el envio del documento al proveedor {}".format(e))

    # def refacturapt_services(self):
    #     if not self.file_send_acknowledgement_electronic_invoice:
    #         raise ValidationError("No se puede generar el evento de recibo del bien o prestaci??n de servicio, porque no se ha generado el acuse de recibo")
    #     if self.file_refacturapt_services:
    #         raise ValidationError("No se puede generar el evento de recibo del bien o prestaci??n de servicio, porque ya se gener?? anteriormente")

    #     user_id = self.env.user
    #     create_date = datetime.datetime.now()

    #     if not self.ref or not self.supplier_invoice_cufe or not self.supplier_invoice_type or not user_id.partner_id.fe_nit \
    #             or not user_id.partner_id.fe_digito_verificacion or not user_id.partner_id.fe_tipo_documento \
    #             or not user_id.partner_id.fe_es_compania or not self.company_id.partner_id.fe_nit \
    #             or not self.company_id.partner_id.fe_digito_verificacion or not self.company_id.partner_id.fe_tipo_documento \
    #             or not self.company_id.partner_id.fe_es_compania or not self.partner_id.fe_nit \
    #             or not self.partner_id.fe_digito_verificacion or not self.partner_id.fe_tipo_documento or \
    #             not self.partner_id.fe_es_compania or not self.journal_id.refacturapt_services_sequence_id:
    #         raise ValidationError(
    #             "Revisar que los siguientes campos no esten vacios: CUFE Factura Proveedor, Tipo factura proveedor, "
    #             "Sequencia ApplicationResponse Acuse Recibo en Diario, Tipo de documento/Nit/Digito Verificacion/"
    #             "Tipo persona en Cliente, Tipo de documento/Nit/Digito Verificacion/Tipo persona en Compa??ia, "
    #             "Tipo de documento/Nit/Digito Verificacion/Tipo persona en Usuario")
    #     nit = str(self.partner_id.fe_nit).zfill(10)
    #     current_year = datetime.datetime.now().replace(tzinfo=pytz.timezone('America/Bogota')).strftime('%Y')
    #     prefix = self.journal_id.refacturapt_services_sequence_id.prefix
    #     consecutivo = int(self.journal_id.refacturapt_services_sequence_id._next_do().replace(prefix, ""))
    #     filename = 'ar{}000{}{}'.format(nit, current_year[-2:], str(hex(consecutivo)).split("x")[1].zfill(8))
    #     invoice = self
    #     key_data = '{}{}{}'.format(
    #         invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin,
    #         prefix + str(consecutivo)
    #     )
    #     sha384 = hashlib.sha384()
    #     sha384.update(key_data.encode())
    #     software_security_code = sha384.hexdigest()

    #     try:
    #         invoice_fe_data = {
    #             'fe_nit': invoice.company_id.partner_id.fe_nit,
    #             'fe_digito_verificacion': invoice.company_id.partner_id.fe_digito_verificacion,
    #             'fe_software_id': invoice.company_id.fe_software_id,
    #             'software_security_code': software_security_code,
    #             'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'de_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'de_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_customer_party_name': saxutils.escape(invoice.company_id.name),
    #             'invoice_customer_identification': self.company_id.partner_id.fe_nit,
    #             'invoice_customer_identification_digit': self.company_id.partner_id.fe_digito_verificacion,
    #             'invoice_customer_responsabilidad_tributaria': self.company_id.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_customer_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.company_id.partner_id.fe_responsabilidad_tributaria),
    #             'invoice_customer_type_person': self.company_id.partner_id.fe_es_compania,
    #             'invoice_customer_document_type': self.company_id.partner_id.fe_tipo_documento,
    #             'invoice_supplier_type_person': self.partner_id.fe_es_compania,
    #             'invoice_supplier_party_name': saxutils.escape(invoice.partner_id.name) if invoice.partner_id.fe_facturador else saxutils.escape(invoice.partner_id.parent_id.name),
    #             'invoice_supplier_identification': self.partner_id.fe_nit,
    #             'invoice_supplier_identification_digit': self.partner_id.fe_digito_verificacion,
    #             'invoice_supplier_document_type': self.partner_id.fe_tipo_documento,
    #             'invoice_supplier_responsabilidad_tributaria': self.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_supplier_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.partner_id.fe_responsabilidad_tributaria),
    #             'refacturaver_id': user_id.partner_id.fe_nit,
    #             'refacturaver_document_type': user_id.partner_id.fe_tipo_documento,
    #             'refacturaver_verification_digit': user_id.partner_id.fe_digito_verificacion,
    #             'refacturaver_first_name': user_id.partner_id.fe_primer_nombre + user_id.partner_id.fe_segundo_nombre if user_id.partner_id.fe_segundo_nombre else user_id.partner_id.fe_primer_nombre,
    #             'refacturaver_second_name': user_id.partner_id.fe_primer_apellido + user_id.partner_id.fe_segundo_apellido if user_id.partner_id.fe_segundo_apellido else user_id.partner_id.fe_primer_apellido,
    #             'application_response_id': prefix + str(consecutivo),
    #             'document_reference': self.ref,
    #             'de_cude': self.generate_cude("032", create_date, prefix + str(consecutivo)),
    #             'profile_execution_cude_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'invoice_cufe': self.supplier_invoice_cufe,
    #             'document_type_reference': self.supplier_invoice_type,
    #         }
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al formar el diccionario de datos {}".format(e))

    #     try:
    #         xml_template = self.get_template_str('../templates/recibo_b&s.xml')
    #         export_template = Template(xml_template)
    #         output = export_template.render(invoice_fe_data)
    #         event_name = 'file_refacturapt_services'
    #         invoice.sudo().write({
    #             event_name: base64.b64encode(output.encode())
    #         })
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al renderizar la plantilla {}".format(e))
    #     try:
    #         self.firmar_factura_electronica(True, filename, event_name)
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en la firma del documento {}".format(e))

    #     try:
    #         self.filename_refacturapt_services = prefix+str(consecutivo)
    #         respuesta, is_valid, validation_code = self.intento_envio_factura_electronica(True, filename, event_name,'032',prefix+str(consecutivo),self.ref)
    #         self[event_name.replace('file', 'answer')] = respuesta
    #         self.env.cr.commit()
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en el envio del documento a la DIAN {}".format(e))

    #     try:
    #         self.event_send_email(True, validation_code,respuesta,filename, event_name, '032', prefix + str(consecutivo),self.ref)
    #         self.email_refacturapt_services = True
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error en el envio del documento al proveedor {}".format(e))

    # def express_acceptance(self):
    #     if not self.file_send_acknowledgement_electronic_invoice:
    #         raise ValidationError("No se puede generar el evento de aceptaci??n expresa, porque no se ha generado el acuse de recibo")
    #     if not self.file_refacturapt_services:
    #         raise ValidationError("No se puede generar el evento de aceptaci??n expresa, porque no se ha generado el acuse de recibo de bienes o servicios")
    #     if self.file_electronic_sales_invoice_claim:
    #         raise ValidationError("No se puede generar el evento de reclamo de la factura de venta, porque ya se rechaz?? anteriormente")
    #     if self.file_express_acceptance:
    #         raise ValidationError("No se puede generar el evento de reclamo de la factura de venta, porque ya se acept?? anteriormente")

    #     user_id = self.env.user
    #     create_date = datetime.datetime.now()

    #     if not self.ref and not self.supplier_invoice_cufe or not self.supplier_invoice_type or not user_id.partner_id.fe_nit \
    #             or not user_id.partner_id.fe_digito_verificacion or not user_id.partner_id.fe_tipo_documento \
    #             or not user_id.partner_id.fe_es_compania or not self.company_id.partner_id.fe_nit \
    #             or not self.company_id.partner_id.fe_digito_verificacion or not self.company_id.partner_id.fe_tipo_documento \
    #             or not self.company_id.partner_id.fe_es_compania or not self.partner_id.fe_nit \
    #             or not self.partner_id.fe_digito_verificacion or not self.partner_id.fe_tipo_documento or \
    #             not self.partner_id.fe_es_compania or not self.journal_id.express_acceptance_sequence_id:
    #         raise ValidationError(
    #             "Revisar que los siguientes campos no esten vacios: CUFE Factura Proveedor, Tipo factura proveedor, "
    #             "Sequencia ApplicationResponse Acuse Recibo en Diario, Tipo de documento/Nit/Digito Verificacion/"
    #             "Tipo persona en Cliente, Tipo de documento/Nit/Digito Verificacion/Tipo persona en Compa??ia, "
    #             "Tipo de documento/Nit/Digito Verificacion/Tipo persona en Usuario")

    #     nit = str(self.partner_id.fe_nit).zfill(10)
    #     current_year = datetime.datetime.now().replace(tzinfo=pytz.timezone('America/Bogota')).strftime('%Y')

    #     prefix = self.journal_id.express_acceptance_sequence_id.prefix
    #     consecutivo = int(self.journal_id.express_acceptance_sequence_id._next_do().replace(prefix, ""))

    #     filename = 'ar{}000{}{}'.format(nit, current_year[-2:], str(hex(int(consecutivo))).split("x")[1].zfill(8))

    #     invoice = self
    #     key_data = '{}{}{}'.format(
    #         invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin,
    #         prefix + str(consecutivo)
    #     )
    #     sha384 = hashlib.sha384()
    #     sha384.update(key_data.encode())
    #     software_security_code = sha384.hexdigest()


    #     try:
    #         invoice_fe_data = {
    #             'fe_nit': invoice.company_id.partner_id.fe_nit,
    #             'fe_digito_verificacion': invoice.company_id.partner_id.fe_digito_verificacion,
    #             'fe_software_id': invoice.company_id.fe_software_id,
    #             'software_security_code': software_security_code,
    #             'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'de_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'de_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_customer_party_name': saxutils.escape(invoice.company_id.name),
    #             'invoice_customer_identification': self.company_id.partner_id.fe_nit,
    #             'invoice_customer_identification_digit': self.company_id.partner_id.fe_digito_verificacion,
    #             'invoice_customer_responsabilidad_tributaria': self.company_id.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_customer_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.company_id.partner_id.fe_responsabilidad_tributaria),
    #             'invoice_customer_type_person': self.company_id.partner_id.fe_es_compania,
    #             'invoice_customer_document_type': self.company_id.partner_id.fe_tipo_documento,
    #             'invoice_supplier_type_person': self.partner_id.fe_es_compania,
    #             'invoice_supplier_party_name': saxutils.escape(invoice.partner_id.name) if invoice.partner_id.fe_facturador else saxutils.escape(invoice.partner_id.parent_id.name),
    #             'invoice_supplier_identification': self.partner_id.fe_nit,
    #             'invoice_supplier_identification_digit': self.partner_id.fe_digito_verificacion,
    #             'invoice_supplier_document_type': self.partner_id.fe_tipo_documento,
    #             'invoice_supplier_responsabilidad_tributaria': self.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_supplier_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.partner_id.fe_responsabilidad_tributaria),
    #             'refacturaver_id': user_id.partner_id.fe_nit,
    #             'refacturaver_document_type': user_id.partner_id.fe_tipo_documento,
    #             'refacturaver_verification_digit': user_id.partner_id.fe_digito_verificacion,
    #             'refacturaver_first_name': user_id.partner_id.fe_primer_nombre + user_id.partner_id.fe_segundo_nombre if user_id.partner_id.fe_segundo_nombre else user_id.partner_id.fe_primer_nombre,
    #             'refacturaver_second_name': user_id.partner_id.fe_primer_apellido + user_id.partner_id.fe_segundo_apellido if user_id.partner_id.fe_segundo_apellido else user_id.partner_id.fe_primer_apellido,
    #             'application_response_id': prefix + str(consecutivo),
    #             'document_reference': self.ref,
    #             'de_cude': self.generate_cude("033", create_date, prefix + str(consecutivo)),
    #             'profile_execution_cude_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'invoice_cufe': self.supplier_invoice_cufe,
    #             'document_type_reference': self.supplier_invoice_type,
    #         }
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al formar el diccionario de datos {}".format(e))

    #     try:
    #         xml_template = self.get_template_str('../templates/aceptacion_expresa.xml')
    #         export_template = Template(xml_template)
    #         output = export_template.render(invoice_fe_data)
    #         event_name = 'file_express_acceptance'
    #         invoice.sudo().write({
    #             event_name: base64.b64encode(output.encode())
    #         })
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al renderizar la plantilla {}".format(e))
    #     try:
    #         self.firmar_factura_electronica(True, filename, event_name)
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en la firma del documento {}".format(e))

    #     try:
    #         self.filename_express_acceptance = prefix+str(consecutivo)
    #         respuesta, is_valid, validation_code = self.intento_envio_factura_electronica(True, filename, event_name,'033',prefix+str(consecutivo),self.ref)
    #         self[event_name.replace('file', 'answer')] = respuesta
    #         self.env.cr.commit()
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en el envio del documento a la DIAN {}".format(e))

    #     try:
    #         self.event_send_email(True, validation_code,respuesta,filename, event_name, '033', prefix + str(consecutivo),self.ref)
    #         self.email_express_acceptance = True
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error en el envio del documento al proveedor {}".format(e))

    # def tacit_acceptance(self):
    #     if self.file_tacit_acceptance:
    #         raise ValidationError("No se puede generar el evento de aceptaci??n t??cita, porque ya se gener?? anteriormente")
    #     if not self.file_send_acknowledgement_electronic_invoice:
    #         raise ValidationError("No se puede generar el evento de aceptaci??n expresa, porque no se ha generado el acuse de recibo")
    #     if not self.file_refacturapt_services:
    #         raise ValidationError("No se puede generar el evento de aceptaci??n expresa, porque no se ha generado el acuse de recibo")

    #     user_id = self.env.user
    #     create_date = datetime.datetime.now()

    #     if not self.customer_invoice_type or not user_id.partner_id.fe_nit or not user_id.partner_id.fe_digito_verificacion \
    #             or not user_id.partner_id.fe_tipo_documento or not user_id.partner_id.fe_es_compania or not self.company_id.partner_id.fe_nit \
    #             or not self.company_id.partner_id.fe_digito_verificacion or not self.company_id.partner_id.fe_tipo_documento or \
    #             not self.company_id.partner_id.fe_es_compania or not self.company_id.partner_id.fe_razon_social or not self.partner_id.fe_nit \
    #             or not self.partner_id.fe_digito_verificacion or not self.partner_id.fe_tipo_documento or not self.partner_id.fe_es_compania or \
    #             not self.partner_id.fe_razon_social or not self.journal_id.tacit_acceptance_sequence_id:
    #         raise ValidationError(
    #             "Revisar que los siguientes campos no esten vacios: Tipo factura cliente,Sequencia ApplicationResponse Aceptacion tacita Diario, Tipo de documento / Nit / Digito Verificacion / Tipo persona / Razon social en Cliente, Tipo de documento / Nit / DigitoVerificacion / Tipo persona / Razon social en Compa??ia, Tipo de documento / Nit / Digito verrificacion / Tipo persona en Usuario")

    #     nit = str(self.partner_id.fe_nit).zfill(10)
    #     current_year = datetime.datetime.now().replace(tzinfo=pytz.timezone('America/Bogota')).strftime('%Y')
    #     prefix = self.journal_id.tacit_acceptance_sequence_id.prefix
    #     consecutivo = int(self.journal_id.tacit_acceptance_sequence_id._next_do().replace(prefix,""))
    #     filename = 'ar{}000{}{}'.format(nit, current_year[-2:], str(hex(consecutivo)).split("x")[1].zfill(8))
    #     invoice = self
    #     key_data = '{}{}{}'.format(
    #         invoice.company_id.fe_software_id, invoice.company_id.fe_software_pin,
    #         prefix+str(consecutivo)
    #     )
    #     sha384 = hashlib.sha384()
    #     sha384.update(key_data.encode())
    #     software_security_code = sha384.hexdigest()

    #     try:
    #         invoice_fe_data = {
    #             'fe_nit': invoice.company_id.partner_id.fe_nit,
    #             'fe_digito_verificacion': invoice.company_id.partner_id.fe_digito_verificacion,
    #             'fe_software_id': invoice.company_id.fe_software_id,
    #             'software_security_code': software_security_code,
    #             'profile_execution_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'de_issue_date': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%Y-%m-%d'),
    #             'de_issue_time': create_date.astimezone(pytz.timezone("America/Bogota")).strftime('%H:%M:%S-05:00'),
    #             'invoice_company_party_name': saxutils.escape(invoice.company_id.name),
    #             'invoice_company_identification': self.company_id.partner_id.fe_nit,
    #             'invoice_company_identification_digit': self.company_id.partner_id.fe_digito_verificacion,
    #             'invoice_company_name': self.company_id.partner_id.fe_razon_social,
    #             'invoice_company_responsabilidad_tributaria': self.company_id.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_company_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.company_id.partner_id.fe_responsabilidad_tributaria),
    #             'invoice_company_type_person': self.company_id.partner_id.fe_es_compania,
    #             'invoice_company_document_type': self.company_id.partner_id.fe_tipo_documento,
    #             'invoice_client_type_person': self.partner_id.fe_es_compania,
    #             'invoice_client_party_name': saxutils.escape(invoice.partner_id.name),
    #             'invoice_client_identification': self.partner_id.fe_nit,
    #             'invoice_client_identification_digit': self.partner_id.fe_digito_verificacion,
    #             'invoice_client_document_type': self.partner_id.fe_tipo_documento,
    #             'invoice_client_name': self.partner_id.fe_razon_social,
    #             'invoice_client_responsabilidad_tributaria': self.partner_id.fe_responsabilidad_tributaria,
    #             'invoice_client_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.partner_id.fe_responsabilidad_tributaria),
    #             'document_reference': self.name,
    #             'document_type_reference': self.customer_invoice_type,
    #             'invoice_mandate_contract': self.invoice_mandate_contract,
    #             'refacturaver_id': user_id.partner_id.fe_nit,
    #             'refacturaver_document_type': user_id.partner_id.fe_tipo_documento,
    #             'refacturaver_verification_digit': user_id.partner_id.fe_digito_verificacion,
    #             'refacturaver_first_name': user_id.partner_id.fe_primer_nombre + user_id.partner_id.fe_segundo_nombre,
    #             'refacturaver_second_name': user_id.partner_id.fe_primer_apellido + user_id.partner_id.fe_segundo_apellido,
    #             'application_response_id': prefix+str(consecutivo),
    #             'de_cude': self.generate_cude("034", create_date, prefix + str(consecutivo)),
    #             'profile_execution_cude_id': self.company_id.fe_tipo_ambiente if self.company_id.fe_tipo_ambiente != '3' else '2',
    #             'invoice_cufe': self.cufe,
    #             'invoice_mandate_type_person': self.mandate_id.fe_es_compania if self.invoice_mandate_contract else "",
    #             'invoice_mandate_party_name': saxutils.escape(invoice.mandate_id.name) if self.invoice_mandate_contract else "",
    #             'invoice_mandate_identification': self.mandate_id.fe_nit if self.invoice_mandate_contract else "",
    #             'invoice_mandate_identification_digit': self.mandate_id.fe_digito_verificacion if self.invoice_mandate_contract else "",
    #             'invoice_mandate_document_type': "NIT" if self.mandate_id.fe_tipo_documento == '31' else "Cedula Ciudadania" if self.invoice_mandate_contract else "",
    #             'invoice_mandate_name': self.mandate_id.fe_razon_social if self.invoice_mandate_contract else "",
    #             'invoice_mandate_responsabilidad_tributaria': self.mandate_id.fe_responsabilidad_tributaria if self.invoice_mandate_contract else "",
    #             'invoice_mandate_responsabilidad_tributaria_text': self.calcular_texto_responsabilidad_tributaria(self.mandate_id.fe_responsabilidad_tributaria) if self.invoice_mandate_contract else "",
    #         }
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al formar el diccionario de datos {}".format(e))

    #     try:
    #         xml_template = self.get_template_str('../templates/aceptacion_tacita_fev.xml')
    #         export_template = Template(xml_template)
    #         output = export_template.render(invoice_fe_data)
    #         event_name = 'file_tacit_acceptance'
    #         invoice.sudo().write({
    #             event_name: base64.b64encode(output.encode())
    #         })
    #     except Exception as e:
    #         raise ValidationError("Se gener?? un error al renderizar la plantilla {}".format(e))
    #     try:
    #         self.firmar_factura_electronica(True, filename, event_name)
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en la firma del documento {}".format(e))

    #     try:
    #         respuesta, is_valid, validation_code = self.intento_envio_factura_electronica(True, filename, event_name,'034',prefix+str(consecutivo),self.name)
    #         self[event_name.replace('file', 'answer')] = respuesta
    #     except Exception as e:
    #         self[event_name] = None
    #         raise ValidationError("Se gener?? un error en el envio del documento a la DIAN {}".format(e))


    # # endregion
    # # region comment '''
    #     """def action_invoice_move_create(self):
    #         #Creates invoice related analytics and financial move lines 
    #         account_move = self.env['account.move']
    #         for inv in self:
    #             if not inv.journal_id.sequence_id:
    #                 raise UserError(('Please define sequence on the journal related to this invoice.'))
    #             if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
    #                 raise UserError(('Please add at least one invoice line.'))
    #             if inv.move_id:
    #                 continue
    #             if not inv.invoice_date:
    #                 inv.write({'invoice_date': fields.Date.context_today(self)})
    #             if not inv.invoice_date_due:
    #                 inv.write({'invoice_date_due': inv.v})
    #             company_currency = inv.company_id.currency_id
    #             # create move lines (one per invoice line + eventual taxes and analytic lines)
    #             iml = inv.invoice_line_move_line_get()
    #             iml += inv.tax_line_move_line_get()
    #             iml += inv.invoice_discount_get()
    #             diff_currency = inv.currency_id != company_currency
    #             # create one move line for the total and possibly adjust the other lines amount
    #             total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)
    #             name = inv.name or ''
    #             if inv.payment_term_id:
    #                 totlines = \
    #                 inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.invoice_date)[0]
    #                 res_amount_currency = total_currency
    #                 for i, t in enumerate(totlines):
    #                     if inv.currency_id != company_currency:
    #                         amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id,
    #                                                                     inv._get_currency_rate_date() or fields.Date.today())
    #                     else:
    #                         amount_currency = False
    #                     # last line: add the diff
    #                     res_amount_currency -= amount_currency or 0
    #                     if i + 1 == len(totlines):
    #                         amount_currency += res_amount_currency
    #                     iml.append({
    #                         'type': 'dest',
    #                         'name': name,
    #                         'price': t[1],
    #                         'account_id': inv.account_id.id,
    #                         'date_maturity': t[0],
    #                         'amount_currency': diff_currency and amount_currency,
    #                         'currency_id': diff_currency and inv.currency_id.id,
    #                         'invoice_id': inv.id
    #                     })
    #             else:
    #                 iml.append({
    #                     'type': 'dest',
    #                     'name': name,
    #                     'price': total,
    #                     'account_id': inv.account_id.id,
    #                     'date_maturity': inv.invoice_date_due,
    #                     'amount_currency': diff_currency and total_currency,
    #                     'currency_id': diff_currency and inv.currency_id.id,
    #                     'invoice_id': inv.id
    #                 })
    #             part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
    #             line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
    #             line = inv.group_lines(iml, line)
    #             line = inv.finalize_invoice_move_lines(line)
    #             date = inv.date or inv.invoice_date
    #             move_vals = {
    #                 'ref': inv.reference,
    #                 'line_ids': line,
    #                 'journal_id': inv.journal_id.id,
    #                 'date': date,
    #                 'narration': inv.comment,
    #             }
    #             move = account_move.create(move_vals)
    #             # Pass invoice in method post: used if you want to get the same
    #             # account move reference when creating the same invoice after a cancelled one:
    #             move.post(invoice=inv)
    #             # make the invoice point to that move
    #             vals = {
    #                 'move_id': move.id,
    #                 'date': date,
    #                 'move_name': move.name,
    #             }
    #             inv.write(vals)
    #         return True
    #         """
    #     # Fin de funci??n Creada
    #     # endregion

    # def reset_acknowledgement_electronic_invoice(self):
    #     if (self.answer_send_acknowledgement_electronic_invoice and 'Procesado Correctamente' not in self.answer_send_acknowledgement_electronic_invoice) or (self.file_send_acknowledgement_electronic_invoice and not self.answer_send_acknowledgement_electronic_invoice):
    #         self.file_send_acknowledgement_electronic_invoice = None
    #         self.answer_send_acknowledgement_electronic_invoice = None
    #     else:
    #         raise ValidationError("No es posible eliminar el evento porque ya est?? procesado correctamente")

    # def reset_electronic_sales_invoice_claim(self):
    #     if (self.answer_electronic_sales_invoice_claim and 'Procesado Correctamente' not in self.answer_electronic_sales_invoice_claim) or (self.file_electronic_sales_invoice_claim and not self.answer_electronic_sales_invoice_claim):
    #         self.file_electronic_sales_invoice_claim = None
    #         self.answer_electronic_sales_invoice_claim = None
    #     else:
    #         raise ValidationError("No es posible eliminar el evento porque ya est?? procesado correctamente")

    # def reset_refacturapt_services(self):
    #     if (self.answer_refacturapt_services and 'Procesado Correctamente' not in self.answer_refacturapt_services) or (self.file_refacturapt_services and not self.answer_refacturapt_services):
    #         self.file_refacturapt_services = None
    #         self.answer_refacturapt_services = None
    #     else:
    #         raise ValidationError("No es posible eliminar el evento porque ya est?? procesado correctamente")

    # def reset_express_acceptance(self):
    #     if (self.answer_express_acceptance and 'Procesado Correctamente' not in self.answer_express_acceptance) or (self.file_express_acceptance and not self.answer_express_acceptance):
    #         self.file_express_acceptance = None
    #         self.answer_express_acceptance = None
    #     else:
    #         raise ValidationError("No es posible eliminar el evento porque ya est?? procesado correctamente")

    # def reset_tacit_acceptance(self):
    #     if (self.answer_tacit_acceptance and 'Procesado Correctamente' not in self.answer_tacit_acceptance) or (self.file_tacit_acceptance and not self.answer_tacit_acceptance):
    #         self.file_tacit_acceptance = None
    #         self.answer_tacit_acceptance = None
    #     else:
    #         raise ValidationError("No es posible eliminar el evento porque ya est?? procesado correctamente")

    # def send_email_acknowledgement_electronic_invoice(self):
    #     if (self.answer_send_acknowledgement_electronic_invoice and 'Procesado Correctamente' not in self.answer_send_acknowledgement_electronic_invoice) or not self.answer_send_acknowledgement_electronic_invoice:
    #         raise ValidationError("No es posible reenviar correo del el evento porque no est?? procesado correctamente")
    #     else:
    #         try:
    #             validation_code = '00' if 'StatusCode: 00' in self.answer_send_acknowledgement_electronic_invoice else ''
    #             self.event_send_email(True, validation_code, "", "", "file_send_acknowledgement_electronic_invoice", '030', self.filename_send_acknowledgement_electronic_invoice,self.ref)
    #             self.email_send_acknowledgement_electronic_invoice = True
    #         except Exception as e:
    #             raise ValidationError("No fue posible enviar el correo: {}".format(e))
            

    # def send_email_electronic_sales_invoice_claim(self):
    #     if (self.answer_electronic_sales_invoice_claim and 'Procesado Correctamente' not in self.answer_electronic_sales_invoice_claim) or not self.answer_electronic_sales_invoice_claim:
    #         raise ValidationError("No es posible reenviar correo del el evento porque no est?? procesado correctamente")
    #     else:
    #         try:
    #             validation_code = '00' if 'StatusCode: 00' in self.answer_electronic_sales_invoice_claim else ''
    #             self.event_send_email(True, validation_code, "", "", "file_electronic_sales_invoice_claim", '031', self.filename_electronic_sales_invoice_claim,self.ref)
    #             self.email_electronic_sales_invoice_claim = True
    #         except Exception as e:
    #             raise ValidationError("No fue posible enviar el correo: {}".format(e))

    # def send_email_refacturapt_services(self):
    #     if (self.answer_refacturapt_services and 'Procesado Correctamente' not in self.answer_refacturapt_services) or not self.answer_refacturapt_services:
    #         raise ValidationError("No es posible reenviar correo del el evento porque no est?? procesado correctamente")
    #     else:
    #         try:
    #             validation_code = '00' if 'StatusCode: 00' in self.answer_refacturapt_services else ''
    #             self.event_send_email(True, validation_code, "", "", "file_refacturapt_services", '032', self.filename_refacturapt_services,self.ref)
    #             self.email_refacturapt_services = True
    #         except Exception as e:
    #             raise ValidationError("No fue posible enviar el correo: {}".format(e))
    # def send_email_express_acceptance(self):
    #     if (self.answer_express_acceptance and 'Procesado Correctamente' not in self.answer_express_acceptance) or not self.answer_express_acceptance:
    #         raise ValidationError("No es posible reenviar correo del el evento porque no est?? procesado correctamente")
    #     else:
    #         try:
    #             validation_code = '00' if 'StatusCode: 00' in self.answer_express_acceptance else ''
    #             self.event_send_email(True, validation_code, "", "", "file_express_acceptance", '033', self.filename_express_acceptance,self.ref)
    #             self.email_express_acceptance = True
    #         except Exception as e:
    #             raise ValidationError("No fue posible enviar el correo: {}".format(e))
    # # region comment '''
    # # def consulta_fe_dian(self):
    # #     response_nsd = {
    # #         'b': 'http://schemas.datacontract.org/2004/07/DianResponse',
    # #     }
    # #     dian_webservice_url = self.env['ir.config_parameter'].search(
    # #         [('key', '=', 'dian.webservice.url')], limit=1).value
    # #
    # #     service = WsdlQueryHelper(
    # #         url=dian_webservice_url,
    # #         template_file=self.get_template_str('../templates/soap_skel.xml'),
    # #         key_file=self.company_id.fe_certificado,
    # #         passphrase=self.company_id.fe_certificado_password
    # #     )
    # #     _logger.info('Consultando estado de validaci??n para factura {}'.format(self.prefix_invoice_number()))
    # #
    # #     if not self.envio_fe_id.track_id:
    # #         raise ValidationError(
    # #             'No se puede realizar la consulta debido a que '
    # #             'la factura no tiene un n??mero de seguimiento asignado por la DIAN'
    # #         )
    # #
    # #     try:
    # #         if len(self.envio_fe_id.track_id) == 96:  # Consulta con CUFE de documento
    # #             response = service.get_status(track_id=self.envio_fe_id.track_id)
    # #         else:
    # #             response = service.get_status_zip(track_id=self.envio_fe_id.track_id)
    # #     except Exception as e:
    # #         _logger.error('No fue posible realizar la consulta a la DIAN. C??digo de error: {}'.format(e))
    # #         raise ValidationError(u'No fue posible realizar la consulta a la DIAN. \n\nC??digo de error: {}'.format(e))
    # #
    # #     xml_content = etree.fromstring(response)
    # #     status_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusMessage']
    # #     status_description = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusDescription']
    # #     validation_status = status_description[0].text if status_message else 'Error'
    # #
    # #     if status_message:
    # #         log_status = status_message[0].text if status_message[0].text else status_description[0].text
    # #     else:
    # #         log_status = 'Error'
    # #
    # #     _logger.info('Respuesta de validaci??n => {}'.format(log_status))
    # #
    # #     if validation_status == 'Procesado Correctamente' and not self.enviada_por_correo:
    # #         _logger.info('Enviando factura {} por correo electr??nico.'.format(self.prefix_invoice_number()))
    # #         self.notificar_correo()
    # #         self.enviada_por_correo = True
    # #
    # #     data = {
    # #         'codigo_respuesta': service.get_response_status_code(),
    # #         'descripcion_estado': status_description[0].text,
    # #         'hora_actual': datetime.datetime.now(),
    # #         'contenido_respuesta': response,
    # #         'nombre_fichero': 'validacion_{}_{}.xml'.format(
    # #             self.number,
    # #             datetime.datetime.now(pytz.timezone("America/Bogota")).strftime('%Y%m%d_%H%M%S')
    # #         ),
    # #     }
    # #
    # #     return data
    # # endregion
    # # region consulta_fe_dian
    # def consulta_fe_dian(self):
    #     response_nsd = {
    #         'b': 'http://schemas.datacontract.org/2004/07/DianResponse',
    #     }
    #     if self.company_id.fe_tipo_ambiente == '1':  # Producci??n
    #         dian_webservice_url = self.env['ir.config_parameter'].sudo().search(
    #             [('key', '=', 'dian.webservice.url')], limit=1).value
    #     else:
    #         dian_webservice_url = self.env['ir.config_parameter'].sudo().search(
    #             [('key', '=', 'dian.webservice.url.pruebas')], limit=1).value

    #     service = WsdlQueryHelper(
    #         url=dian_webservice_url,
    #         template_file=self.get_template_str('../templates/soap_skel.xml'),
    #         key_file=self.company_id.fe_certificado,
    #         passphrase=self.company_id.fe_certificado_password
    #     )
    #     _logger.info('Consultando estado de validaci??n para factura {}'.format(self.prefix_invoice_number()))

    #     try:
    #         response = service.get_status(track_id=self.cufe)
    #     except Exception as e:
    #         _logger.error('No fue posible realizar la consulta a la DIAN. C??digo de error: {}'.format(e))
    #         raise ValidationError(u'No fue posible realizar la consulta a la DIAN. \n\nC??digo de error: {}'.format(e))

    #     xml_content = etree.fromstring(response)
    #     status_message = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusMessage']
    #     status_description = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusDescription']
    #     #status_text = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}ErrorMessage']
    #     status_code = [item for item in xml_content.iter() if item.tag == '{' + response_nsd['b'] + '}StatusCode']
    #     validation_status = status_message[0].text if status_message else 'Error'
    #     #validation_error = status_text[0].text if status_message else 'Error'
    #     validation_code = status_code[0].text if status_message else 'Error'

    #     if status_message:
    #         log_status = status_message[0].text if status_message[0].text else status_description[0].text
    #     else:
    #         log_status = 'Error'

    #     _logger.info('Respuesta de validaci??n => {}'.format(log_status))

    #     self.envio_fe_id.write({
    #         'codigo_respuesta_validacion': status_code[0].text,
    #         'respuesta_validacion': status_description[0].text if status_description[0].text and status_description[0].text!= None else log_status,
    #         'fecha_validacion': datetime.datetime.now(),
    #         'nombre_archivo_validacion': 'validacion_{}_{}.xml'.format(
    #             self.name,
    #             datetime.datetime.now(pytz.timezone("America/Bogota")).strftime('%Y%m%d_%H%M%S')
    #         ),
    #         'archivo_validacion': base64.b64encode(response.encode('utf-8'))
    #     })

    #     data = {
    #         'codigo_respuesta': status_code[0].text,
    #         'descripcion_estado': status_description[0].text if status_description[0].text and status_description[0].text!= None else log_status,
    #         'hora_actual': datetime.datetime.now(),
    #         'contenido_respuesta': response,
    #         'nombre_fichero': 'validacion_{}_{}.xml'.format(
    #             self.name,
    #             datetime.datetime.now(pytz.timezone("America/Bogota")).strftime('%Y%m%d_%H%M%S')
    #         ),
    #     }

    #     output = self.generar_attachment_xml()
    #     self.sudo().write({'attachment_file': base64.b64encode(output.encode())})
    #     _logger.info('Attachmen Document generado')

    #     config = {
    #         'policy_id': self.company_id.fe_url_politica_firma,
    #         'policy_name': self.company_id.fe_descripcion_polica_firma,
    #         'policy_remote': self.company_id.fe_archivo_polica_firma,
    #         'key_file': self.company_id.fe_certificado,
    #         'key_file_password': self.company_id.fe_certificado_password,
    #     }

    #     firmado = sign(base64.b64encode(output.encode()), config)

    #     _logger.info('Attachmen Document firmado')

    #     template = self.env.ref('l10n_co_factura.account_invoices_fe')

    #     render_template = template.render_qweb_pdf([self.id])

    #     buff = BytesIO()
    #     zip_file = zipfile.ZipFile(buff, mode='w')

    #     zip_content = BytesIO()
    #     zip_content.write(firmado)
    #     zip_file.writestr(self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.xml', zip_content.getvalue())

    #     zip_content = BytesIO()
    #     zip_content.write(base64.b64decode(base64.b64encode(render_template[0])))
    #     zip_file.writestr(self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.pdf', zip_content.getvalue())

    #     zip_file.close()

    #     zipped_file = base64.b64encode(buff.getvalue())

    #     self.sudo().write({'zipped_file': zipped_file})

    #     buff.close()

    #     if not self.attachment_id:
    #         attachment = self.env['ir.attachment'].create({
    #             'name': self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.zip',
    #             'res_model': 'account.invoice',
    #             'res_id': self.id,
    #             'store_fname': self.filename.replace('fv', 'ad').replace('nc', 'ad').replace('nd', 'ad') + '.zip',
    #             'mimetype': 'zip',
    #             'datas': zipped_file,
    #             'type': 'binary',
    #         })

    #         self.sudo().write({'attachment_id': attachment.id})

    #     if validation_code == '00' and not self.enviada_por_correo:
    #         _logger.info('Enviando factura {} por correo electr??nico.'.format(self.prefix_invoice_number()))
    #         self.notificar_correo()
    #         self.enviada_por_correo = True
    #         val = {
    #             'company_id': self.company_id.id,
    #             'actividad': 'Envio de Factura al Cliente',
    #             'fecha_hora': self.write_date,
    #             'factura': self.id,
    #             'estado': self.state,
    #             'type': 'Factura Electronica' if self.type=='out_invoice' and not self.es_nota_debito else 'Nota Debito' if self.type=='out_invoice' and self.es_nota_debito else'Nota Credito',
    #             'estado_validacion': self.fe_approved
    #         }
    #         self.env['l10n_co_factura.history'].create(val)

    #     if validation_code != '00' and not self.enviada_error:
    #         _logger.info('Error en factura {} descripcion enviada por correo electr??nico.'.format(self.prefix_invoice_number()))
    #         self.notificar_correo_error(self.prefix_invoice_number(), validation_status)
    #         self.enviada_error = True
    #         val = {
    #             'company_id': self.company_id.id,
    #             'actividad': 'Envio de Factura al Cliente',
    #             'fecha_hora': self.write_date,
    #             'factura': self.id,
    #             'estado': self.state,
    #             'type': 'Factura Electronica' if self.type == 'out_invoice' and not self.es_nota_debito else 'Nota Debito' if self.type == 'out_invoice' and self.es_nota_debito else 'Nota Credito',
    #             'estado_validacion': self.fe_approved
    #         }
    #         self.env['l10n_co_factura.history'].create(val)

    #     return data

    # # endregion
    # # region get_base_url
    # def get_base_url(self):
    #     external_url = self.env['ir.config_parameter'].sudo().get_param(
    #         'email.button.url'
    #     )

    #     if external_url and external_url != u' ':
    #         return external_url

    #     else:
    #         base_url = self.env['ir.config_parameter'].sudo().get_param(
    #             'web.base.url'
    #         )
    #         return base_url

    # # endregion
    # # region get_attachment
    # def get_attachment(self):
    #     if not self.attachment_id:
    #         raise ValidationError('No se encontr?? el archivo adjunto.')

    #     return self.attachment_id.id

    # # endregion
    # # region cron_envio_dian
    # @api.model
    # def cron_envio_dian(self):
    #     invoices = self.env['account.move'].sudo().search([
    #         ('state', '=', 'posted'),
    #         ('enviada', '=', False),
    #         ('zipped_file', '!=', False),
    #     ])

    #     for invoice in invoices:
    #         if not invoice.enviada and \
    #                 invoice.state == 'posted' and \
    #                 invoice.company_resolucion_id.tipo == 'facturacion-electronica':

    #             try:
    #                 _logger.info('=> Enviando factura No. {}'.format(invoice.name))
    #                 invoice.intento_envio_factura_electronica()
    #                 self.env.cr.commit()
    #             except Exception as e:
    #                 _logger.error('[!] Error al enviar la factura {} - Excepci??n: {}'.format(invoice.name, e))

    #     invoices_72 = self.env['account.move'].sudo().search([
    #         ('state', '=', 'posted'),
    #         ('enviada', '=', True),
    #         ('envio_fe_id', '!=', None),
    #         ('fe_approved', '=','sin-calificacion')
    #     ])

    #     for id_envio in invoices_72:
    #         if id_envio.fecha_entrega:
    #             hora_comparar = id_envio.fecha_entrega + datetime.timedelta(hours=72)
    #             hora = hora_comparar - datetime.datetime.now()
    #             horas = int(hora.total_seconds())
    #             if horas < 0 and id_envio.envio_fe_id.codigo_respuesta_validacion == '00':
    #                 id_envio.write({'fe_approved':'aprobada_sistema'})

    # # endregion
    # #region reconsulta dian
    # @api.model
    # def cron_reconsulta_dian(self):
    #     envios = self.env['l10n_co_factura.envio_fe'].search([
    #         ('respuesta_validacion', 'in',
    #          ['Validaci??n contiene errores en campos mandatorios.', '', False, None])
    #     ], limit=30)

    #     for envio in envios:
    #         try:
    #             _logger.info('=> Consultando estado de factura No. {}'.format(envio.invoice_id.name))
    #             envio.consulta_fe_dian()
    #         except Exception as e:
    #             _logger.info('[!] Error al validar la factura {} - Excepci??n: {}'.format(envio.invoice_id.name, e))
    # #endregion
    # # region _default_journal_fe
    # @api.model
    # @api.depends('partner_id')
    # def _default_journal_fe(self):
    #     return self._get_default_journal()

    # # endregion
    # # region compute_journal_fe
    # @api.onchange('fe_sucursal')
    # def compute_journal_fe(self):
    #     for invoice in self:
    #         invoice.journal_id = invoice._get_default_journal()

    # # endregion
    # # region _get_default_journal
    # @api.model
    # def _get_default_journal(self):
    #     journal_id = super(Invoice, self)._get_default_journal()
    #     # Si la factura por defecto es una nota d??bito, busca de nuevo el diario por defecto

    #     if ((journal_id and journal_id.categoria == 'nota-debito') or (journal_id and self.credited_invoice_id)) and not self._context.get('default_journal_id', False):
    #         if self.fe_sucursal and self.fe_sucursal.journal_id_nd:
    #             journal_id = self.fe_sucursal.journal_id_nd
    #         else:
    #             domain = [
    #                 ('type', '=', journal_id.type),
    #                 ('company_id', '=', journal_id.company_id.id),
    #                 ('categoria', '=', 'nota-debito'),
    #             ]
    #             company_currency_id = journal_id.company_id.currency_id.id
    #             currency_id = self._context.get('default_currency_id') or company_currency_id
    #             currency_clause = [('currency_id', '=', currency_id)]
    #             if currency_id == company_currency_id:
    #                 currency_clause = ['|', ('currency_id', '=', False)] + currency_clause
    #             journal_id = self.env['account.journal'].sudo().search(domain + currency_clause, limit=1)

    #             return journal_id
    #     # if self.es_factura_electronica and self.fe_habilitar_facturacion_related:

    #     if self.fe_sucursal and self.fe_sucursal.journal_id_fv:
    #         journal_id = self.fe_sucursal.journal_id_fv

    #     return journal_id

    # # endregion
    # # region journal_id
    # journal_id = fields.Many2one(
    #     'account.journal',
    #     string='Journal',
    #     required=True,
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    #     default=_default_journal_fe,
    #     domain="""
    #         [('type', 'in', {'out_invoice': ['sale'], 
    #         'out_refund': ['sale'], 'in_refund': ['purchase'], 
    #         'in_invoice': ['purchase']}.get(type, [])), 
    #         ('company_id', '=', company_id)]
    #         """
    # )
    # #endregion
    # # region action_invoice_sent
    # def action_invoice_sent(self):
    #     """ Open a window to compose an email, with the edi invoice template
    #         message loaded by default
    #     """
    #     if self.company_id.fe_habilitar_facturacion:
    #         self.ensure_one()
    #         template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
    #         #template = self.env.ref('l10n_co_factura.approve_invoice_fe_email_template')
    #         lang = get_lang(self.env)
    #         if template and template.lang:lang = template._render_template(template.lang, 'account.move', self.id)
    #         compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
    #         ctx = dict(
    #             default_model='account.move',
    #             default_res_id=self.id,
    #             default_use_template=bool(template),
    #             default_template_id=template and template.id or False,
    #             default_composition_mode='comment',
    #             mark_invoice_as_sent=True,
    #             custom_layout="mail.mail_notification_paynow",
    #             model_description=self.type_name,
    #             force_email=True
    #         )

    #         archivos_fe = self.env['l10n_co_factura.fe_archivos_email'].sudo().search([
    #             ('invoice_id', '=', self.id)
    #         ])

    #         zip_file = self.attachment_id

    #         archivos_fe_ids = []

    #         for datos in archivos_fe:
    #             attachment_archivos_fe = self.env['ir.attachment'].sudo().search([('res_field', '!=', None),
    #             ('res_id', '=', datos.id),
    #             ('res_model', '=','l10n_co_factura.fe_archivos_email'),],
    #             limit=1)
    #             attachment_archivos_fe.name = datos.nombre_archivo_envio

    #             if attachment_archivos_fe:
    #                 archivos_fe_ids.append(attachment_archivos_fe.id)

    #         archivos_fe_ids.append(zip_file.id)

    #         if template:
    #             template.email_from = str(self.fe_company_email_from)
    #             template.attachment_ids = [(5, 0, [])]
    #             if archivos_fe_ids:
    #                 template.attachment_ids = [(6, 0, archivos_fe_ids)]
    #             template.attachment_ids = [(5, 0, [])]

    #         return {
    #             'name': _('Send Invoice'),
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'account.invoice.send',
    #             'views': [(compose_form.id, 'form')],
    #             'view_id': compose_form.id,
    #             'target': 'new',
    #             'context': ctx,
    #         }
    #     else:
    #         super(Invoice, self).action_invoice_sent()
    # # endregion
    
    # def generate_cude(self, tipo_evento, create_date, numde):
    #     numde = numde
    #     fecfac = create_date.astimezone(pytz.timezone('America/Bogota')).strftime('%Y-%m-%d')
    #     horfac = create_date.astimezone(pytz.timezone('America/Bogota')).strftime('%H:%M:%S-05:00')
    #     nitfe = self.company_id.partner_id.fe_nit
    #     docadq = self.partner_id.fe_nit if tipo_evento != '034' else '800197268'
    #     responsecode = tipo_evento
    #     id = self.ref if self.type in ('in_invoice','in_refound') else self.name
    #     documenttypecode = self.supplier_invoice_type if self.type in ('in_invoice','in_refound') else self.customer_invoice_type
    #     pinsoftware = self.company_id.fe_software_pin
    #     cude = numde+fecfac+horfac+nitfe+docadq+responsecode+id+documenttypecode+pinsoftware
    #     _logger.info(f"\ncude {cude}\n")
    #     sha384 = hashlib.sha384()
    #     sha384.update(cude.encode())
    #     cude = sha384.hexdigest()

    #     return cude

    # def calculate_text_supplier_claim_concept(self,id):
    #     if id == '01':
    #         return 'Documento con inconsistencias'
    #     elif id == '03':
    #         return 'Mercanc??a no entregada totalmente'
    #     elif id == '03':
    #         return 'Mercanc??a no entregada parcialmente'
    #     elif id == '04':
    #         return 'Servicio no prestado'
    #     else:
    #         return ''

class InvoiceLine(models.Model):
    _inherit = "account.move.line"
    line_price_reference = fields.Float(string='Precio de referencia')
    line_trade_sample_price = fields.Selection(string='Tipo precio de referencia',
                                               related='move_id.trade_sample_price')
    line_trade_sample = fields.Boolean(string='Muestra comercial', related='move_id.invoice_trade_sample')


    invoice_discount_text = fields.Selection(
        selection=[
            ('00', 'Descuento no condicionado'),
            ('01', 'Descuento condicionado')
        ],
        string='Motivo de Descuento',
    )

    #Se agrega en el onchange_product_id la asignaci??n al precio de referencia
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            line.tax_ids = line._get_computed_taxes()
            line.product_uom_id = line._get_computed_uom()
            line.price_unit = line._get_computed_price_unit()

            # Manage the fiscal position after that and adapt the price_unit.
            # E.g. mapping a price-included-tax to a price-excluded-tax must
            # remove the tax amount from the price_unit.
            # However, mapping a price-included tax to another price-included tax must preserve the balance but
            # adapt the price_unit to the new tax.
            # E.g. mapping a 10% price-included tax to a 20% price-included tax for a price_unit of 110 should preserve
            # 100 as balance but set 120 as price_unit.
            if line.tax_ids and line.move_id.fiscal_position_id:
                line.price_unit = line._get_price_total_and_subtotal()['price_subtotal']
                line.tax_ids = line.move_id.fiscal_position_id.map_tax(line.tax_ids._origin,
                                                                       partner=line.move_id.partner_id)
                accounting_vals = line._get_fields_onchange_subtotal(price_subtotal=line.price_unit,
                                                                     currency=line.move_id.company_currency_id)
                balance = accounting_vals['debit'] - accounting_vals['credit']
                line.price_unit = line._get_fields_onchange_balance(balance=balance).get('price_unit', line.price_unit)

            # Convert the unit price to the invoice's currency.
            company = line.move_id.company_id
            line.price_unit = company.currency_id._convert(line.price_unit, line.move_id.currency_id, company,
                                                           line.move_id.date)
            line.line_price_reference = line.price_unit

        if len(self) == 1:
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_uom_id.category_id.id)]}}

    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        ''' Recompute the 'price_unit' depending of the unit of measure. '''
        price_unit = self._get_computed_price_unit()

        # See '_onchange_product_id' for details.
        taxes = self._get_computed_taxes()
        if taxes and self.move_id.fiscal_position_id:
            price_subtotal = self._get_price_total_and_subtotal(price_unit=price_unit, taxes=taxes)['price_subtotal']
            accounting_vals = self._get_fields_onchange_subtotal(price_subtotal=price_subtotal,
                                                                 currency=self.move_id.company_currency_id)
            balance = accounting_vals['debit'] - accounting_vals['credit']
            price_unit = self._get_fields_onchange_balance(balance=balance).get('price_unit', price_unit)

        # Convert the unit price to the invoice's currency.
        company = self.move_id.company_id
        self.price_unit = company.currency_id._convert(price_unit, self.move_id.currency_id, company, self.move_id.date)
        self.line_price_reference = self.price_unit
