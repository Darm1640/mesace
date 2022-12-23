# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    as_activo_100 = fields.Boolean(string='Generar 100 activos de movimiento', default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['as_activo_100'] = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_activo_100'))
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_activo_100', self.as_activo_100)
        super(ResConfigSettings, self).set_values()