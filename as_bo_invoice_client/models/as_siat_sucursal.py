# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _
from . import as_siat_utility as as_utility

# Sucursal
class as_siat_sucursal(models.Model):
    _name = 'as.siat.sucursal'
    _description = "Modelo que guarda la informacion de las sucursales"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Nombre")
    as_system_id = fields.Many2one('as.siat.codigo.sistema', string="Código Sistema")
    as_office_number = fields.Char(string="Numero de sucursal", default='0', help='Casa Matriz: 0, Sucursal: 1,2,..,n')
    as_pdv_ids = fields.One2many('as.siat.punto.venta', 'as_branch_office', string="Puntos de Ventas")
    as_cufd = fields.One2many('as.siat.cufd', 'as_branch_office', string="Cufd")
    as_cuis = fields.Char(string="CUIS Principal")
    as_type = fields.Many2one('as.siat.catalogos', string="Tipo Punto de venta", domain="[('as_group.name', '=', 'PUNTO_VENTA')]", required=True, default=lambda self: self.env['as.siat.catalogos'].search([('as_group.name', '=', 'PUNTO_VENTA')],limit=1))   

    def as_request_cuis_sale(self):
        for pdv in self.as_pdv_ids:
            json = {
                    "codigoSucursal": self.as_office_number,
                    "codigoPuntoVenta": pdv.as_code
                }
            respuesta = as_utility.as_process_json('CUIS',json,self.env.user.id,self.as_system_id.as_token_ahorasoft,'Obtener CUIS')
            if respuesta[0] and respuesta[1]['success']:
                if 'values' in respuesta[1]:
                    if pdv.as_code == '0':
                        self.as_cuis = respuesta[1]['values']['cuis']
                pdv.as_cuis = respuesta[1]['values']['cuis']
                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
            else:
                if 'values' in respuesta[1]:
                    if pdv.as_code == '0':
                        self.as_cuis = respuesta[1]['values']
                    pdv.as_cuis = respuesta[1]['values']
                mensaje = as_utility.as_format_error(respuesta[1])
            self.message_post(body = str(mensaje), content_subtype='html')  

    def as_request_point_sale(self):
        json = {
            "codigoSucursal": self.as_office_number,
            "codigoTipoPuntoVenta": self.as_type.as_code,
            "cuis": self.as_cuis,
            "descripcion": "Punto de Venta Creado",
            "nombrePuntoVenta": "Punto de Venta Creado",
            }
        respuesta = as_utility.as_process_json('PDV',json,self.env.user.id,self.as_system_id.as_token_ahorasoft,'Crear Punto de Venta')
        if respuesta[0] and respuesta[1]['success']:
            if 'values' in respuesta[1]:
                valores = respuesta[1]['values']
                pdv = {
                    'active' : True,
                    'name' : valores['puntoventa'],
                    'as_code' : valores['puntoventa'],
                    'as_branch_office' : self.id,
                    'as_type' : self.as_type.id,
                }
                self.env['as.siat.punto.venta'].create(pdv)
            mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
        else:
            mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
        self.message_post(body = str(mensaje), content_subtype='html')  

    def as_request_cufd(self):
        self.env.cr.execute("UPDATE as_siat_cufd SET active = False")
        for pdv in self.as_pdv_ids:
            json = {
                    "codigoSucursal": self.as_office_number,
                    "codigoPuntoVenta": pdv.as_code
                }
            respuesta = as_utility.as_process_json('CUFD',json,self.env.user.id,self.as_system_id.as_token_ahorasoft,'Obtener CUFD')
            if respuesta[0] and respuesta[1]['success']:
                if 'values' in respuesta[1]:
                    valores = respuesta[1]['values']
                    cufd = {
                        'active' : True,
                        'as_cufd_value' : valores['codigo'],
                        'as_expire_date' : valores['fechaVigencia'],
                        'as_branch_office' : self.id,
                        'as_pdv_id' : pdv.id,
                        'as_control_code' : valores['codigoControl'],
                        'as_address' : valores['direccion'],
                    }

                    self.env['as.siat.cufd'].create(cufd)
                    body="<b>Transaccion CUFD exitosa:</b> <br>%s" %(cufd)
                    self.message_post(body = body, content_subtype='html')
                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
            else:
                if type(respuesta[1]) == '':
                    mensaje = as_utility.as_format_error(respuesta[1])
                else:
                    mensaje = as_utility.as_format_error(respuesta[1]['mensaje'])
            self.message_post(body = str(mensaje), content_subtype='html')  