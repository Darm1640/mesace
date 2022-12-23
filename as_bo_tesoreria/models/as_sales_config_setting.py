# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    as_limite_pago = fields.Float('Generacion de facturas hasta el', default=30)
    as_amount_access = fields.Float('Monto para Calcular Diferencia', default=1.50)
    as_modalidad  = fields.Selection([('Factura','Factura'),('Venta','Venta'),('Factura-Venta','Factura-Venta')] ,'Modalidad Documento Tesoreria', help=u'Tipo de documento para tesoreria.', default='Factura')
    as_itf_catidad = fields.Float(string = 'Configuración de % ITF', default=0.3) 

  
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['as_limite_pago'] = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limite_pago'))
        res['as_amount_access'] = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_amount_access'))
        res['as_modalidad'] = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_modalidad'))
        res['as_itf_catidad'] = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_itf_catidad'))
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_limite_pago', self.as_limite_pago)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_amount_access', self.as_amount_access)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_modalidad', self.as_modalidad)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_itf_catidad', self.as_itf_catidad)
        super(ResConfigSettings, self).set_values()