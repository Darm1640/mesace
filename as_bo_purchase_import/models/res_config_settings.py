# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_purchase_import_template = fields.Boolean("Cost Templates", implied_group='as_bo_purchase_import.group_purchase_import_template')
    default_purchase_template_id = fields.Many2one('stock.landed.template', default_model='purchase.order', string='Default Template')
    module_cost_quotation_builder = fields.Boolean("Template Builder")
    as_mostrar_fecha = fields.Boolean("Mostrar Fecha en Reporte de Gastos")

    @api.onchange('group_purchase_import_template')
    def _onchange_group_purchase_import_template(self):
        if not self.group_purchase_import_template:
            self.module_cost_quotation_builder = False
            self.default_purchase_template_id = False
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['as_mostrar_fecha'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_mostrar_fecha')
      
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_mostrar_fecha', self.as_mostrar_fecha)
        super(ResConfigSettings, self).set_values()