# -*- coding: utf-8 -*-
##############################################################################

from datetime import datetime, timedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.exceptions import UserError
from odoo.tools.translate import _
import base64
from odoo import netsvc
from odoo import tools
from time import mktime
import logging
from datetime import datetime
from odoo import api, fields, models
from . import as_siat_utility as as_utility

class as_product_detail_wiz(models.TransientModel):
    _name="as.anular.factura"
    _description = "Duplicar venta by AhoraSoft"

    def _default_sistema(self):
        if len(self.env.user.as_system_certificate) > 0:
            return self.env.user.as_system_certificate[0]
        else:
            return False

    def _default_sucursal(self):
        if len(self.env.user.as_branch_office)> 0: 
            return self.env.user.as_branch_office[0]
        else:
            return False
            
    def _default_pdv(self):
        if len(self.env.user.as_pdv_ids)> 0: 
            return self.env.user.as_pdv_ids[0]
        else:
            return False

    as_fiscal_document_code = fields.Many2one('as.siat.catalogos', required=True, string="Tipo documento fiscal", domain="[('as_group', '=', 'TIPO_FACTURA')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'TIPO_FACTURA'),('as_code','=','1')],limit=1))
    as_sector_type = fields.Many2one('as.siat.catalogos', required=True, string="Tipo documento sector", domain="[('as_group', '=', 'DOCUMENTO_SECTOR')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'DOCUMENTO_SECTOR'),('as_code','=','1')],limit=1))
    as_emission_type = fields.Many2one('as.siat.catalogos', string="Tipo emision", required=True, domain="[('as_group', '=', 'EMISION')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','1')],limit=1))
    as_codigo_sistema = fields.Many2one('as.siat.codigo.sistema', string="Codigo Sistema", default=_default_sistema, required=True,)
    as_branch_office = fields.Many2one('as.siat.sucursal', string="Sucursal", default=_default_sucursal, required=True)
    as_pdv_id = fields.Many2one('as.siat.punto.venta', string="Punto de Venta", default=_default_pdv, required=True)
    as_motivo_anulacion = fields.Many2one('as.siat.catalogos', required=True,string="Tipo documento identidad", domain="[('as_group', '=', 'MOTIVO_ANULACION')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'MOTIVO_ANULACION'),('as_code','=','1')],limit=1))
    as_cufd = fields.Char( string="CUFD",required=True)
    as_cuf = fields.Char( string="CUF",required=True)

    @api.onchange('as_pdv_id')
    def as_get_as_pdv_id(self):
        for page in self:
            if len(page.as_pdv_id.as_cufd)>=1:
                page.as_cufd = page.as_pdv_id.as_cufd[0].as_cufd_value

    def get_sale_process(self):
        for invoice in self:
            json = {
                    "codigoSucursal": str(invoice.as_branch_office.as_office_number),
                    "codigoPuntoVenta":  str(invoice.as_pdv_id.as_code),
                    "codigoMotivo": str(invoice.as_motivo_anulacion.as_code),
                    "codigoDocumentoSector": str(invoice.as_sector_type.as_code),
                    "codigoEmision": str(invoice.as_emission_type.as_code),
                    "tipoFacturaDocumento": str(invoice.as_fiscal_document_code.as_code),
                    "cufd": str(invoice.as_cufd),
                    "cuf": str(invoice.as_cuf),
                  
                }
            respuesta = as_utility.as_process_json('Factura Cancelar',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Factura Cancelar',self)
            if respuesta[0] and respuesta[1]['success']:
                if 'factura' in respuesta[1]:
                    valores = respuesta[1]['factura']
                    if valores['codigoEstado'] == '905':
                        mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
                        invoice.as_pdv_id.message_post(body = str(mensaje), content_subtype='html') 
                    else:
                        if type(valores['mensajesList']) == type([]):
                            for error in valores['mensajesList']:
                                mensaje = as_utility.as_format_error(error['codigo']+': '+error['descripcion'])
                                invoice.as_pdv_id.message_post(body = str(mensaje), content_subtype='html') 
                        else:
                            mensaje = as_utility.as_format_error(valores['mensajesList']['codigo']+': '+valores['mensajesList']['descripcion'])
                            invoice.as_pdv_id.message_post(body = str(mensaje), content_subtype='html') 
            else:
                invoice.as_pdv_id.message_post(body = str(respuesta[1]['mensaje']), content_subtype='html') 
    