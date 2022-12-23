# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from . import as_siat_utility as as_utility

class as_siat_catalogos(models.Model):
    _name = 'as.siat.catalogos'
    _description = "Modelo generico para guardar los diferentes valores de tipos de facturas, emision, mensaje SOAP, leyendas, etc. Segun sea necesario"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name  = fields.Char(string="Descripcion", required=True)
    as_group = fields.Many2one('as.siat.group', string="Agrupador")
    as_code  = fields.Char(string="Código", required=True)
    as_actividad = fields.Char(string="Actividad Economica")
    as_respuesta  = fields.Char(string="Respuesta")


class as_siat_group(models.Model):
    _name = 'as.siat.group'
    _description = "Modelo para guardar agrupadores de catálogo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name  = fields.Char(string="Titulo", required=True)
    as_endpoint_name  = fields.Char(string="Catálogo en Endpoint", required=True)
    as_index = fields.Char(string="Index en Endpoint", required=True)

    def action_register_catalogos(self):
        as_values = self.env['as.siat.group'].search([('id','in',tuple(self._context['active_ids']))])
        certificado = self.env.user.as_system_certificate
        if len(certificado) < 1:
            raise UserError(_("Debe tener cargado certificado el usuario."))
        sucursal = self.env.user.as_branch_office
        if len(sucursal) < 1:
            raise UserError(_("Debe tener cargado sucursal el usuario."))
        pdv = self.env.user.as_pdv_ids
        if len(pdv) < 1:
            raise UserError(_("Debe tener cargado punto de venta el usuario."))
        for group in as_values:
            json = {
                    "codigoPuntoVenta": pdv[0].as_code,
                    "codigoSucursal": sucursal[0].as_office_number,
                    "catalogo": group.as_endpoint_name
                }
            respuesta = as_utility.as_process_json('Catalogos',json,self.env.user.id,certificado.as_token_ahorasoft,'Obtener Catálogos')
            if respuesta[0] and respuesta[1]['success']:
                cont = 1
                if 'values' in respuesta[1]:
                    for lista in dict(respuesta[1]['values']):
                        separator = group.as_index.split(',')
                        valores = respuesta[1]['values'][lista][separator[0]][separator[1]]
                        for catalogo in valores:
                            if lista == 'ns2:sincronizarListaLeyendasFacturaResponse':
                                values = self.env['as.siat.catalogos'].search([('as_group','=',group.id),('as_code','=',str(cont))],limit=1)
                            else:
                                values = self.env['as.siat.catalogos'].search([('as_group','=',group.id),('as_code','=',catalogo[separator[2]])],limit=1)
                            if not values:
                                if lista == 'ns2:sincronizarListaActividadesDocumentoSectorResponse':
                                    self.env['as.siat.catalogos'].create({
                                        'name':catalogo['tipoDocumentoSector'],
                                        'as_group':group.id,
                                        'as_code':catalogo[separator[2]]
                                    })       
                                elif lista == 'ns2:sincronizarListaProductosServiciosResponse':
                                    self.env['as.siat.catalogos'].create({
                                        'name':catalogo['descripcionProducto'],
                                        'as_group':group.id,
                                        'as_code':catalogo[separator[2]],
                                        'as_actividad':catalogo['codigoActividad'],
                                    })                                       
                                elif lista == 'ns2:sincronizarListaLeyendasFacturaResponse':
                                    self.env['as.siat.catalogos'].create({
                                        'name':catalogo['descripcionLeyenda'],
                                        'as_group':group.id,
                                        'as_code':cont,
                                        'as_actividad':catalogo[separator[2]],
                                    })                              
                                else:
                                    self.env['as.siat.catalogos'].create({
                                        'name':catalogo['descripcion'],
                                        'as_group':group.id,
                                        'as_code':catalogo[separator[2]]
                                    })         
                                cont+=1
                            else:
                                if lista == 'ns2:sincronizarListaProductosServiciosResponse':
                                    values.write({
                                        'name':catalogo['descripcionProducto'],
                                        'as_code':catalogo[separator[2]],
                                        'as_actividad':catalogo['codigoActividad'],
                                    }) 


            else:
                raise UserError(_("No se puedo establecer comunicación con el SIAT."))




