# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _
from . import as_siat_utility as as_utility

# Sucursal
class as_siat_codigo_sistema(models.Model):
    _name = 'as.siat.codigo.sistema'
    _description = "Modelo para almacenar codigo de sistema o visor proporcionado"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Codigo de Sistema")
    active = fields.Boolean(default=True)
    as_nit = fields.Char(string="NIT")
    as_razon_social = fields.Char(string="Razon Social")
    as_login = fields.Char(string="Login")
    as_password = fields.Char(string="Password")
    as_token = fields.Char(string="Token SIAT")
    as_token_ahorasoft = fields.Char(string="Token AHORASOFT")
    as_leyenda = fields.Char(string="Leyenda")
    as_branch_offices = fields.One2many('as.siat.sucursal', 'as_system_id', string="Sucursales")
    as_date_expire = fields.Date(string="Fecha de expiración")


    def consulta_certificado(self):
        self.message_post(body = str('Certificado Activo'), content_subtype='html')  
    
    def resquest_auth(self):
        for sys in self:
            json = {
                "login": sys.as_login,
                "nit": sys.as_nit,
                "password": sys.as_password,
                "token": sys.as_token,
                "fecha_vencimiento": str(sys.as_date_expire)
            }
            respuesta = as_utility.as_process_json('Token',json,sys.env.user.id,False,'Obtener Token Ahorasoft')
            if respuesta[0] and respuesta[1]['success']:
                sys.as_token_ahorasoft = respuesta[1]['token_ahorasoft']
                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
            else:
                mensaje = as_utility.as_format_error(respuesta[1])
            sys.message_post(body = str(mensaje), content_subtype='html')  
            return respuesta
