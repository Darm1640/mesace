# -*- coding: utf-8 -*-
import logging
import odoo
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _

# Heredar el modelo de clientes y agregarle los campos adicionales
class product_template(models.Model):
    _inherit = 'product.template'

    as_config = fields.Boolean(string="Dias de vida util", compute='_compute_as_config',default=False)
    as_gift_card = fields.Boolean("Gift card", default=False)

    # @api.multi
    def _compute_as_config(self):
        aux = 0
        gift_card = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_gift_card'))

        for pp in self:
            pp.as_config = gift_card