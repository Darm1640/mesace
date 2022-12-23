# -*- coding: utf-8 -*-

import time

import odoo
from odoo import api, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import psycopg2
from . import as_amount_to_text_es
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_compare
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)
#clase heredada de purchase order para agregar funciones de creacion de facturas y campos adicionales
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    as_fecha_entrega = fields.Date(string='Fecha de entrega')
    as_payment_term_id = fields.Many2one('account.payment.term', 'Terminos de pago')
    as_payment_quirer = fields.Many2one('as.payment.acquirer', 'Medio de pago')
    as_solicitante = fields.Many2one('res.partner', string= "Solicitante")
    
    """ Calcula monto de acuerdo al tipo de factura """
    
    @api.depends('as_tipo_factura','amount_total')
    def _compute_tipo_factura(self):
        for invoice in self:
            monto = 0.0
            if invoice.as_tipo_factura:
                monto = invoice.amount_total * invoice.as_tipo_factura.as_factor
            invoice.update({'as_monto_exento' : monto})
    """Trae datos del partner al cambiar el campo"""
    @api.onchange('partner_id')
    def change_razon_social_nit(self):
        last_purchase= self.env['purchase.order'].search([],order='create_date desc', limit=1)
        if self.partner_id:
            self.as_nit_compra = self.partner_id.vat or 'S/N'
            self.as_razon_social_compra = self.partner_id.as_razon_social or 'S/R'
            if last_purchase:
                self.as_numero_autorizacion_compra = last_purchase.as_numero_autorizacion_compra or ''

    @api.onchange('as_tipo_retencion')
    def change_tipo_compra(self):
        if self.as_tipo_retencion.id == 4:
            self.as_tipo_de_compra = ''

    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion = {
            'nombre_empresa' : self.company_id.name or '',
            'nit' : self.company_id.vat or '',
            'direccion1' : self.company_id.street or '',
            'telefono' : self.company_id.phone or '',
            'ciudad' : self.company_id.city or '',
            'pais' : self.company_id.country_id.name or '',
        }
        info = diccionario_dosificacion[str(requerido)]
        return info

    # @api.multi
    # def _lineas_ordenadas(self):
    #     type_order = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_type_order_report')
    #     if not type_order or type_order == 'Ninguno':
    #         order_lines =self.order_line
    #     else:
    #         order_lines= self.env['purchase.order.line'].search([('order_id','=',self.id)],order=(str(type_order)+" asc"))
    #     return order_lines

    """Copia la fecha a d ela orden a ala fecha de la factura"""
    @api.onchange('date_order')
    def change_date_rder(self):
        if self.date_order:
            self.as_fecha_factura = self.date_order

    """Formatea el campo codigo de control"""
    @api.onchange('as_codigo_control_compra')
    def change_as_codigo_control_compra(self):
        cont=0
        if self.as_codigo_control_compra:
            codigo=self.as_codigo_control_compra
            codigo= codigo.replace('-','')
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

    tipo_de_compra = [
        ('1','Actividad gravada'),
        ('2','Actividad no gravada'),
        ('3','Sujetas a proporcionalidad'),
        ('4','Exportaciones'),
        ('5','Interno/Exportaciones'),
        ('6','')
    ]

    # @api.onchange('as_tipo_retencion','order_line')
    # def as_quitar_impuesto_retencion(self):
    #     retenciones = sin_retencion = self.env['as.tipo.retencion'].search([('id','=',self.as_tipo_retencion.id)])
    #     sin_retencion = self.env['as.tipo.retencion'].search([('as_iue', '=', 0),('as_it', '=', 0),('as_iva', '=', 0)],limit=1)
    #     if self.as_tipo_retencion != sin_retencion and self.as_tipo_retencion:
    #         for line in self.order_line:
    #             line.update({
    #                 'taxes_id':'',
    #             })

    """Campos adicionales agregados"""
    as_tipo_documento  = fields.Selection([('Factura','Factura'),('Prefactura/Recibo','Prefactura/Recibo')] ,'Tipo de documento', help=u'Tipo de documento que pertenece la factura.', default='Prefactura/Recibo')
    as_nit_compra = fields.Char('NIT')
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion')
    as_razon_social_compra = fields.Char('Razon Social', help="Nombre o Razón Social de la Factura de Proveedor.")
    as_numero_factura_compra  = fields.Char(string='No Factura', help='Numero de factura.')
    as_codigo_control_compra = fields.Char('Codigo Control')
    as_numero_autorizacion_compra  = fields.Char(string='No Autorizacion', help='Numero de Autorizacion.')
    as_tipo_factura  = fields.Many2one('as.tipo.factura',string='Tipo de Factura', help=u'Tipo de factura para el registro de libro de compra y calculo del monto exento automatico.')
    as_monto_exento = fields.Float('Monto Exento.',store=True, readonly=True, compute='_compute_tipo_factura', help=u'Saldo que se tiene de la factura en bolivianos.', default=0)
    as_fecha_factura = fields.Datetime(string='Fecha de Factura', readonly=True, index=True, default=fields.Datetime.now)
    # ew_tipo_compra = fields.Selection([('Local', 'Local'), ('Importacion', 'Importacion')], 'Tipo compra', help=u'Tipo de compra para diferenciar si es operacion local o de importacion.', default='Local')
    as_move_id = fields.Many2one('account.move', string="Comprobante", help=u'Cuenta que detalle si la venta ya tiene su comprobante generado.')
    as_tipo_de_compra = fields.Selection(selection=tipo_de_compra, string="Tipo de compra", default='1',
        help="Tipo de compra para libro de compras Ejemplo:\n1: Actividad gravada \n2:Actividad no gravada \n3:Sujetas a proporcionalidad \n4:Exportaciones \n5:Interno/Exportaciones ")
        # Lector Codigo QR
    as_scan_qr = fields.Char(string="QR factura", help="Click aqui para que el cursor lea el codigo de QR de la factura de compra")
    as_numero_dui = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.')
    """Funcion para el scaner del qr en la orden de compra"""
    @api.onchange('as_scan_qr')
    def escanear_codigo_qr(self):
        if self.as_scan_qr:
            array = (self.as_scan_qr).split('|')
            if len(array) != 12:
                raise UserError(_("Formato de QR invalido"))
            self.as_nit_compra = array[0]
            self.as_numero_factura_compra = str(int(array[1]))
            self.as_numero_autorizacion_compra = array[2]
            fecha = array[3].split("/")
            self.as_fecha_factura = fecha[2] +"-"+ fecha[1] + "-" + fecha[0]
            self.as_codigo_control_compra = array[6]
            self.as_scan_qr = None

    # """Migra los datos de la orden de compra a la factura"""
    # @api.multi
    # def action_view_invoice(self, invoices=False):
    #     factura_confirmada = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_facturas_confirmadas'))
    #     ingreso_confirmado = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_ingreso_confirmado'))
    #     action = self.env.ref('account.action_move_in_invoice_type')
    #     result = action.read()[0]
    #     create_bill = self.env.context.get('create_bill', False)

    #     id_facturas = []
    #     for order in self:
    #         if order.picking_ids and ingreso_confirmado:
    #             for line in order.order_line:
    #                 if line.product_qty != line.qty_received and (line.product_id.type != 'service'):
    #                     raise UserError(_("Confirme los ingresos al almacen, para poder generar la factura"))
    #         if order.as_tipo_documento == 'Factura': 
    #             if ((not order.as_tipo_documento or not order.as_nit_compra) or 
    #                 (not order.as_razon_social_compra) or 
    #                 (not order.as_codigo_control_compra or not order.as_numero_autorizacion_compra) or 
    #                 (not order.as_tipo_factura or not order.partner_id) or 
    #                 (not order.as_fecha_factura or not order.currency_id)) and not order.as_tipo_de_compra:
    #                 raise UserError(_("Por favor registre los datos necesarios para la factura, en 'Entregas y Facturas'"))

    #         # order.order_line._update_received_qty()
    #         result['context'] = {
    #             'type': 'in_invoice',
    #             'default_purchase_id': order.id,
    #             'default_currency_id': order.currency_id.id,
    #             'default_company_id': order.company_id.id,
    #             'default_partner_id': order.partner_id.id,
    #             'default_purchase_id': order.id,
    #             'default_account_id': order.partner_id.property_account_payable_id.id,
    #             'default_date_invoice' : order.as_fecha_factura or (datetime.now()).strftime('%Y-%m-%d'),
    #             'default_as_tipo_documento' : order.as_tipo_documento,
    #             # 'default_as_tipo_retencion' : order.as_tipo_retencion.id,
    #             'default_as_nit' : order.as_nit_compra or 'S/N',
    #             'default_as_razon_social' : order.as_razon_social_compra or 'S/R',
    #             'default_reference' : order.partner_ref or '',
    #             'default_as_numero_dui' : order.as_numero_dui or '',
    #             'default_as_numero_factura_compra' : order.as_numero_factura_compra or None,
    #             'default_as_codigo_control_compra' : order.as_codigo_control_compra or '0',
    #             'default_as_numero_autorizacion_compra' : order.as_numero_autorizacion_compra or None,
    #             'default_as_tipo_factura' : order.as_tipo_factura.id or None,
    #             'default_as_monto_exento' : order.as_monto_exento or 0,
    #             'default_as_tipo_de_compra' : order.as_tipo_de_compra,
    #             'default_origin' : order.name,
    #             'default_reference' : order.partner_ref,
    #             }
    #         result['context']['as_nit']=order.as_nit_compra or 'S/N'
    #         # if "as_tipo_retencion" in order._fields:
    #         #     result['context']['as_tipo_retencion'] = order.as_tipo_retencion.id or None
    #         if factura_confirmada:
    #             result['context']['state'] = 'open'

    #     # override the context to get rid of the default filtering
    #     # choose the view_mode accordingly
    #     if len(self.invoice_ids) > 1 and not create_bill:
    #         result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
    #     else:
    #         res = self.env.ref('account.invoice_supplier_form', False)
    #         result['views'] = [(res and res.id or False, 'form')]
    #         # Do not set an invoice_id if we want to create a new bill.
    #         if not create_bill:
    #             result['res_id'] = self.invoice_ids.id or False
    #     return result
    """Se obtiene el numero de factura"""
    def obtener_numeros_facturas(self, po_name):
        nros_facturas = ''
        facturas = self.env['account.move'].sudo().search([('origin', '=', po_name)])
        for res in facturas:
            if nros_facturas != '' and res.as_numero_factura_compra:
                nros_facturas = str(nros_facturas)+', '+str(res.as_numero_factura_compra)
            elif nros_facturas == '' and res.as_numero_factura_compra:
                nros_facturas = str(res.as_numero_factura_compra)
        return nros_facturas

    def convertir_numero_a_literal(self, amount):
        moneda = self.currency_id.currency_unit_label
        amt_en = as_amount_to_text_es.amount_to_text(amount, moneda)
        return amt_en
    
    
    def extraer_firma_solicitante(self):
        if self.as_solicitante:
            res_users = self.env['res.users'].sudo().search([('partner_id', '=', self.as_solicitante.id)])
            if res_users:
                hr_employee = self.env['hr.employee'].sudo().search([('user_id', '=', res_users.id)])
                return hr_employee.id
    
    def extraer_lineas_compra(self):
        listaventas=[]
        listatotales=[]
        listageneral=[]
        total_neto=0.00
        order_line = self.env['purchase.order.line'].sudo().search([('order_id', '=', self.id)])
        if order_line:
            for line in order_line:
                cant=line.product_qty
                udm=line.product_uom.name
                nro_parte=line.product_id.product_part_num
                product=line.product_id.name
                precio=line.price_unit
                total=cant*precio
                total_neto+=total
                vals={
                'cantidad':cant,
                'udm':udm,
                'nro_aprte':nro_parte,
                'product':product,
                'precio':precio,
                'total':total,
                }
                listaventas.append(vals)  
        return listaventas
    
    def extraer_subtotal_lineas_compra(self, requerido):
        total_neto=0.00
        subtotal=0.00
        descuento=0.00
        order_line = self.env['purchase.order.line'].sudo().search([('order_id', '=', self.id)])
        if order_line:
            for y in order_line:
                cant=y.product_qty
                precio=y.price_unit
                total=cant*precio
                total_neto+=total
                subtotal += y.price_subtotal
                descuento += y.as_descuento_linea
            valor_total=total_neto
        json={
            'totalitos':valor_total,
            'subtotal':subtotal,
            'descuento':descuento,
            'total_con_descuento':valor_total - descuento,
        }
        total_neto = json[str(requerido)]
        return total_neto
    
    def extraer_referencia_factura(self,requerido):
        valores=self.env['account.move'].sudo().search([('invoice_origin', '=', self.name)])
        if valores:
            refrencia=valores.ref
        else:
            refrencia=''
        json={
            'ref':refrencia
        }
        total_neto = json[str(requerido)]
        return total_neto
            
class PurchaseOrderLine(models.Model):
    """ Se agregan los campos a continuacion al modelo purchase order line"""
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    default_code = fields.Char('Reference', related='product_id.default_code',store=True)
    as_stock_purchase = fields.Float(string="Stock")
    route_id = fields.Many2one('stock.location', 'Ubicacion')

    # @api.depends('order_id.state', 'move_ids.state')
    # def _compute_qty_received(self):
    #     productuom = self.env['uom.uom']
    #     for line in self:
    #         if line.order_id.state not in ['purchase', 'done']:
    #             line.qty_received = 0.0
    #             continue
    #         if line.product_id.type not in ['consu', 'product']:
    #             line.qty_received = line.product_qty
    #             continue
    #         bom_delivered = self.sudo()._get_bom_delivered(line.sudo())
    #         if bom_delivered and any(bom_delivered.values()):
    #             total = line.product_qty
    #         elif bom_delivered:
    #             total = 0.0
    #         else:
    #             total = 0.0
    #             for move in line.move_ids:
    #                 if move.state == 'done':
    #                     if move.product_uom != line.product_uom:
    #                         total += productuom._compute_quantity(move.product_uom, move.product_uom_qty, line.product_uom)
    #                     else:
    #                         total += move.product_uom_qty
    #         line.qty_received = total
    