# -*- coding: utf-8 -*-
from odoo import api, fields, models

# Configuracion del modulo en el formulario general de configuraciones por modulos
class AsWhatsappConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    as_default_gateway = [('chatapi', 'Chat API'), ('wablas', 'Wablas')]

    as_whatsapp_wablas_url = fields.Char('Wablas URL')
    as_whatsapp_wablas_token = fields.Char('Wablas Token')

    as_whatsapp_chatapi_url = fields.Char('Chatapi URL')
    as_whatsapp_chatapi_token = fields.Char('Chatapi Token')

    as_whatsapp_default_gateway = fields.Selection(as_default_gateway, 'Gateway por defecto', default="wablas")    

    # Obtener valores del modelo ir.config.parameter
    @api.model
    def get_values(self):
        res = super(AsWhatsappConfigSettings, self).get_values()
        # Wablas
        res['as_whatsapp_wablas_url'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_wablas_url')
        res['as_whatsapp_wablas_token'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_wablas_token')
        # CHATAPI
        res['as_whatsapp_chatapi_url'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_chatapi_url')
        res['as_whatsapp_chatapi_token'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_chatapi_token')
        
        # Default
        res['as_whatsapp_default_gateway'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_default_gateway')
        return res

    # Guardar valores del modelo ir.config.parameter
    @api.model
    def set_values(self):
        super(AsWhatsappConfigSettings, self).set_values()
        # Wablas
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_whatsapp_wablas_url', self.as_whatsapp_wablas_url)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_whatsapp_wablas_token', self.as_whatsapp_wablas_token)
        # Chatapi
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_whatsapp_chatapi_url', self.as_whatsapp_chatapi_url)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_whatsapp_chatapi_token', self.as_whatsapp_chatapi_token)

        # default
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_whatsapp_default_gateway', self.as_whatsapp_default_gateway)        