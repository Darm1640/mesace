# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    as_actividad = fields.Many2one('as.siat.catalogos', string="Actividades Económicas", domain="[('as_group', '=', 'ACTIVIDAD_NIT')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'ACTIVIDAD_NIT')],limit=1))
    as_product_service = fields.Many2one('as.siat.catalogos', string="Productos/Servicios", domain="[('as_group', '=', 'PRODUCTOS_SERVIVIOS')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'PRODUCTOS_SERVIVIOS')],limit=1))
    as_numero_serie = fields.Char(string="Numero de serie")
    as_numero_imei = fields.Char(string="Numero Imei")
    
class Uom(models.Model):
    _inherit = 'uom.uom'

    as_uom = fields.Many2one('as.siat.catalogos', string="Unidad de medida SIN", domain="[('as_group', '=', 'UNIDAD_MEDIDA')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'UNIDAD_MEDIDA')],limit=1))