# -*- coding: utf-8 -*-
from random import randint
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
import requests
import urllib3
import base64
import io
from io import StringIO
import tarfile
import gzip
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import xmltodict
import pprint
import dateutil.parser
import json
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from . import as_siat_utility as as_utility
from dateutil.relativedelta import relativedelta

class as_send_massive_invoices(models.Model):
    _name = 'as.send.massive.invoice'
    _inherit = ["mail.thread"]
    _description = "Envio masivo de paquetes de facturas y facturas de hasta 2000"

    def _default_sistema(self):
        type_inv = self._context.get('default_move_type') or self._context.get('move_type')
        if type_inv == 'out_invoice' and len(self.env.user.as_system_certificate) >0:
            return self.env.user.as_system_certificate[0]

    def _default_sucursal(self):
        type_inv = self._context.get('default_move_type') or self._context.get('move_type')
        if type_inv == 'out_invoice' and len(self.env.user.as_branch_office) >0:
            return self.env.user.as_branch_office[0]

    def _default_pdv(self):
        type_inv = self._context.get('default_move_type') or self._context.get('move_type')
        if type_inv == 'out_invoice' and len(self.env.user.as_pdv_ids) >0:
            return self.env.user.as_pdv_ids[0]

    name = fields.Char(string="Titulo")
    as_type_mode = fields.Selection(string='Tipo de Envio',selection=[('packet','Paquete Contingencia'),('massive','Envio Masivo')])
    as_codigo_sistema = fields.Many2one('as.siat.codigo.sistema', string="Codigo Sistema", default=_default_sistema)
    as_sucursal = fields.Many2one('as.siat.sucursal', string="Surcursal", default=_default_sucursal)
    as_pdv_id = fields.Many2one('as.siat.punto.venta', string="Puntos de Venta", default=_default_pdv)
    as_invoice_move_ids = fields.Many2many('account.move', string="Facturas")
    #contingencia
    as_cont_date_start = fields.Datetime(string="Fecha Inicio Contingencia", default=datetime.now())
    as_cont_date_end = fields.Datetime(string="Fecha Fin Contingencia", default=datetime.now())
    as_cont_reason = fields.Many2one('as.siat.catalogos', string="Tipo emision", domain="[('as_group', '=', 'EVENTOS_SIGNIFICATIVOS')]", required=True, default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'EVENTOS_SIGNIFICATIVOS'),('as_code','=','1')],limit=1))
    as_cont_cafc = fields.Many2one('as.cafc', string="CAFC")
    as_cont_cudf = fields.Char(string="Cufd de Contingencia")
    as_cont_note = fields.Char(string="Descripcion del Evento Ocurrido")
    as_cont_code = fields.Char(string="Código de Evento Significativo")
    as_event_code = fields.Char(string="ID transaccional del Evento")
    as_package_code = fields.Char(string="Código Paquete")
    as_package_valid_code = fields.Char(string="Código Paquete Validado")
    as_cantidad = fields.Integer(string="Cantidad de Facturas")
    as_fiscal_document_code = fields.Many2one('as.siat.catalogos', string="Tipo documento fiscal", domain="[('as_group', '=', 'TIPO_FACTURA')]",default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'TIPO_FACTURA'),('as_code','=','1')],limit=1))
    as_sector_type = fields.Many2one('as.siat.catalogos', string="Tipo documento sector", domain="[('as_group', '=', 'DOCUMENTO_SECTOR')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'DOCUMENTO_SECTOR'),('as_code','=','1')],limit=1))
    as_emission_type = fields.Many2one('as.siat.catalogos', string="Tipo emision", domain="[('as_group', '=', 'EMISION')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','2')],limit=1))
    state = fields.Selection(string='Estado',selection=[('draft','Borrador'),('cola','En Cola'),('event','Evento Creado'),('fuera','Fuera de Tiempo'),('pendiente','Pendiente'),('validado','Validado')],default="draft")
    xml_evento = fields.Char(string="XML evento")
    xml_recepcion = fields.Char(string="XML Recepcion")
    xml_validacion = fields.Char(string="XML Validación")
    as_numero = fields.Boolean(string="Numero facturas")
    as_automatico = fields.Boolean(string="Paquete Automático")
    as_regenerar = fields.Boolean(string="Regenerar XML de Facturas")

    @api.onchange('as_pdv_id')
    def as_get_cufd(self):
        if len(self.as_pdv_id.as_cufd) > 0:
            self.as_cont_cudf = self.as_pdv_id.as_cufd[0].as_cufd_value

    def _sync_adyen_cron(self):
        contingencias = self.env['as.send.massive.invoice'].search([('as_automatico','=',True),('state', 'not in', ('draft','fuera','validado'))])
        as_out_line = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_out_line'))
        if not as_out_line:
            for packet in contingencias:
                now = fields.Datetime.now()
                fecha = packet.as_cont_date_end
                comprobacion = now - fecha
                if comprobacion.days >= 2:
                    packet.state = 'fuera'
                else:
                    if packet.state == 'cola':
                        packet.as_create_evento_significativo()
                    if packet.state == 'event': 
                        packet.as_send_package()
                    if packet.state == 'pendiente': 
                        packet.as_validate_package()
                self.env.cr.commit()

    def _sync_adyen_cron_in_cola(self):
        paquetes = self.env['as.send.massive.invoice'].search([('state','=','draft'),('as_automatico','=',True)])
        for pack in paquetes:
            if pack.verificar_comunicacion():         
                pack.state = 'cola'
                self.env.cr.commit()


    def verificar_comunicacion(self):
        mensaje = ''
        json = {}
        as_out_line = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_out_line'))
        if not as_out_line:
            respuesta = as_utility.as_process_json('Verifica Comunicación',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Verifica Comunicación')
            if respuesta[0] and respuesta[1]['success']:
                return True
            else:
                return False
        else:
            return False

    def as_get_draft(self):
        self.state = 'draft'


    @api.onchange('as_type_mode')
    def as_get_onchange(self):
        if self.as_type_mode == 'packet':
            self.as_emission_type = self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','2')],limit=1)
        else:
            self.as_emission_type = self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','3')],limit=1)


    def as_validate_event(self):
        self.state='event'
        
   
    def as_create_evento_significativo(self):
        for contingencia in self:
            if contingencia.as_type_mode == 'packet':
                if not self.as_event_code:
                    if self.as_cont_cafc and self.as_cont_reason.as_code in ('1','2','3','4'):
                        raise UserError(_("No puede crear un evento con contingencias 1,2,3,4 y cafc seleccionado"))
                    if not self.as_cont_cafc and self.as_cont_reason.as_code in ('5','6','7'):
                        raise UserError(_("No puede crear un evento con contingencias 5,6,7 sin CAFC"))
                    
                    mensaje = ''
                    fechai = (contingencia.as_cont_date_start-relativedelta(hours=4))
                    fechaf = (contingencia.as_cont_date_end-relativedelta(hours=4))
                    fin = as_utility.date2timezone(dateutil.parser.parse(str(fechaf)))
                    inicio = as_utility.date2timezone(dateutil.parser.parse(str(fechai)))
                    cufd_evento = str(contingencia.as_pdv_id.as_cufd[0].as_cufd_value)
                    if contingencia.as_cont_cudf:
                        cufd_evento = str(contingencia.as_cont_cudf)
                    json = {
                            "codigoSucursal": str(contingencia.as_sucursal.as_office_number),
                            "codigoPuntoVenta":  str(contingencia.as_pdv_id.as_code),
                            "codigoMotivoEvento": str(contingencia.as_cont_reason.as_code),
                            "cufdEvento" : cufd_evento,
                            "fechaHoraFinEvento" : str(fin),
                            "fechaHoraInicioEvento" : str(inicio),
                            "descripcion" : str(self.as_cont_note),
                        }
                    respuesta = as_utility.as_process_json('Crear Contingencia',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Crear Contingencia',self)
                    if respuesta[0] and respuesta[1]['success']:
                        if 'codigo' in respuesta[1] and 'factura' in respuesta[1]:
                            self.as_event_code = respuesta[1]['codigo']
                            self.as_cont_code = respuesta[1]['factura']['ns2:registroEventoSignificativoResponse']['RespuestaListaEventos']['codigoRecepcionEventoSignificativo']
                            self.xml_evento = respuesta[1]['xml']
                            mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
                        else:
                            mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
                            self.xml_evento = respuesta[1]['xml']
                    else:
                        mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
                else:
                    mensaje = as_utility.as_format_success('Evento reutilizado!')
                self.message_post(body = str(mensaje), content_subtype='html')  
            else:
                self.as_send_package()
            if self.as_cont_code:
                self.state = 'event'
            self.env.cr.commit()



    def as_send_package(self):
        mensaje = ''
        now = datetime.now() - timedelta(hours=4)
        fceha_envio = as_utility.date2timezone(dateutil.parser.parse(str(now)))
        if self.as_type_mode == 'packet':
            now = fields.Datetime.now()
            fecha = self.as_cont_date_end
            comprobacion = now - fecha
            if comprobacion.days >= 2:
                self.state = 'fuera'
            if self.as_cont_cafc and self.as_cont_reason.as_code in ('1','2','3','4'):
                raise UserError(_("No puede crear un evento con contingencias 1,2,3,4 y cafc seleccionado"))
            if not self.as_cont_cafc and self.as_cont_reason.as_code in ('5','6','7'):
                raise UserError(_("No puede crear un evento con contingencias 5,6,7 sin CAFC"))
            if self.as_cont_cafc and self.as_cont_reason.as_code not in ('1','2','3','4'):
                for inv in self.as_invoice_move_ids:
                    if inv.as_cont_cafc != self.as_cont_cafc:
                        raise UserError(_("EL CAFC del paquete no coincide con el de las facturas empaquetadas"))
                    # inv.as_invoice_number = self.as_cont_cafc.as_proximo
                    # inv.as_cont_cafc = self.as_cont_cafc
                    # inv.as_cafc = self.as_cont_cafc.name
                    # self.as_cont_cafc.as_proximo = self.as_cont_cafc.as_proximo+1
                    # inv.as_reenviar_move()
                    # self.as_numero = True
            invoice_compress = []
            for inv in self.as_invoice_move_ids: 
                if self.as_regenerar:
                    inv.as_generate_invoice_regenerar(True)
                inv.as_cont_cafc = self.as_cont_cafc
                invoice_compress.append({'idtransaccion':inv.as_idtransaccion})
            
            json = {
                    "codigoSucursal": str(self.as_sucursal.as_office_number),
                    "codigoPuntoVenta":  str(self.as_pdv_id.as_code),
                    "codigoEmision":  str(self.as_emission_type.as_code),
                    "tipoFacturaDocumento":  str(self.as_fiscal_document_code.as_code),
                    "codigoDocumentoSector":  str(self.as_sector_type.as_code),
                    "cantidadFacturas":  str(len(self.as_invoice_move_ids)),
                    "codigoEvento":  str(self.as_event_code),
                    "facturas":  invoice_compress,
                }
            if self.as_cont_reason.as_code not in ('1','2','3','4'):
                json['cafc'] = self.as_cont_cafc.name
            respuesta = as_utility.as_process_json('Recepción Envio Contingencia',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Recepción Envio Contingencia',self)
            if respuesta[0] and respuesta[1]['success']:
                if 'codigo' in respuesta[1] and 'factura' in respuesta[1]:
                    valores = respuesta[1]['factura']['ns2:recepcionPaqueteFacturaResponse']['RespuestaServicioFacturacion']
                    if valores['codigoEstado'] == '901':
                        self.as_package_code = respuesta[1]['codigo']
                        self.xml_recepcion = respuesta[1]['xml']
                        self.state = 'pendiente'
                        mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
                    else:
                        if type(valores['mensajesList']) == type([]):
                            for error in valores['mensajesList']:
                                mensaje = as_utility.as_format_error(error['codigo']+': '+error['descripcion'])
                                self.message_post(body = str(mensaje), content_subtype='html') 
                        else:
                            mensaje = as_utility.as_format_error(valores['mensajesList']['codigo']+': '+valores['mensajesList']['descripcion'])
                            self.message_post(body = str(mensaje), content_subtype='html') 
                else:
                    mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
                    self.xml_recepcion = respuesta[1]['xml']
            else:
                # self.xml_recepcion = respuesta[1]['xml']
                mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
        else:
            mensaje = ''
            invoice_compress = []
            for inv in self.as_invoice_move_ids: 
                invoice_compress.append({'idtransaccion':inv.as_idtransaccion})
        
            json = {
                    "codigoSucursal": str(self.as_sucursal.as_office_number),
                    "codigoPuntoVenta":  str(self.as_pdv_id.as_code),
                    "codigoEmision":  str(self.as_emission_type.as_code),
                    "tipoFacturaDocumento":  str(self.as_fiscal_document_code.as_code),
                    "codigoDocumentoSector":  str(self.as_sector_type.as_code),
                    "cantidadFacturas":  str(len(self.as_invoice_move_ids)),
                    "facturas":  invoice_compress,
                }
            respuesta = as_utility.as_process_json('Recepción Envio Masivo',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Recepción Envio Masivo',self)
            if respuesta[0] and respuesta[1]['success']:
                if respuesta[1]['factura']['codigoEstado'] == '901':
                    self.as_package_code = respuesta[1]['codigo']
                    self.xml_recepcion = respuesta[1]['xml']
                    self.state = 'pendiente'
                    mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
                else:
                    if type(valores['mensajesList']) == type([]):
                        for error in valores['mensajesList']:
                            mensaje = as_utility.as_format_error(error['codigo']+': '+error['descripcion'])
                            self.message_post(body = str(mensaje), content_subtype='html') 
                    else:
                        mensaje = as_utility.as_format_error(valores['mensajesList']['codigo']+': '+valores['mensajesList']['descripcion'])
                        self.message_post(body = str(mensaje), content_subtype='html') 

                    mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
                    self.xml_recepcion = respuesta[1]['xml']
            else:
                mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
        self.message_post(body = str(mensaje), content_subtype='html')  
        self.env.cr.commit()

    def as_validate_package(self):
        mensaje = ''
        json = {
                "codigo": str(self.as_package_code),
            }
        if self.as_type_mode == 'packet':
            respuesta = as_utility.as_process_json('Validación Envio Contingencia',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Validación Envio Contingencia',self)
        else:
            respuesta = as_utility.as_process_json('Validación Envio Masivo',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Validación Envio Masivo',self)

        if respuesta[0] and respuesta[1]['success']:
            valores = respuesta[1]['factura']['ns2:validacionRecepcionPaqueteFacturaResponse']['RespuestaServicioFacturacion']
            if valores['codigoEstado'] == '908':
                self.as_package_valid_code = valores['codigoRecepcion']
                self.xml_validacion = respuesta[1]['xml']
                self.state = 'validado'
                for inv in self.as_invoice_move_ids:
                    inv.as_state_siat = 'accepted'
                    if self.as_cont_cafc:
                        inv.as_adjustment_invoice()
                        inv.action_move_send()
                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
            else:
                self.state = 'validado'
                if type(valores['mensajesList']) == type([]):
                    for error in valores['mensajesList']:
                        mensaje = as_utility.as_format_error(error['codigo']+': '+error['descripcion'])
                        self.message_post(body = str(mensaje), content_subtype='html') 
                else:
                    mensaje = as_utility.as_format_error(valores['mensajesList']['codigo']+': '+valores['mensajesList']['descripcion'])
                    self.message_post(body = str(mensaje), content_subtype='html') 
        else:
            mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
        self.message_post(body = str(mensaje), content_subtype='html')  
        self.env.cr.commit()
