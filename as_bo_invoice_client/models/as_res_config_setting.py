# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    as_url_api = fields.Char(string='URL Api Facturación',default='') 
    as_number_end_invoice = fields.Integer(string = 'Dias Limite de Cancelación de Facturas',default=10) 
    as_version = fields.Selection([
            ('V1', 'V1'),
            ('V2', 'V2'),
            ('V3', 'V3'),
        ], string="Versión de Facturación")
    as_limit_nota = fields.Integer(string = 'Meses Limites para generar notas de Debito-Credito',default=18) 
    as_limit_amount = fields.Float(string = 'Monto limite para parametros de NIT/CI Social Social',default=1000) 
    as_timeout_inv = fields.Integer(string='Limite Timeout',default=15) 
    as_out_line = fields.Boolean(string='Sacar sistema de Linea',default=False) 

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['as_url_api'] = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_url_api'))
        res['as_number_end_invoice'] = int(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_number_end_invoice'))
        res['as_version'] = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_version'))
        res['as_limit_nota'] = int(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limit_nota'))
        res['as_limit_amount'] = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limit_amount'))
        res['as_timeout_inv'] = int(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_timeout_inv'))
        res['as_out_line'] = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_out_line'))
        
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_url_api', self.as_url_api)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_number_end_invoice', self.as_number_end_invoice)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_version', self.as_version)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_limit_nota', self.as_limit_nota)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_limit_amount', self.as_limit_amount)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_timeout_inv', self.as_timeout_inv)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_out_line', self.as_out_line)
        super(ResConfigSettings, self).set_values()
