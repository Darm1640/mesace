# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class as_res_currency(models.Model):
    _inherit = "res.currency"


    as_currencysiat = fields.Many2one('as.siat.catalogos', string="Moneda SIN", domain="[('as_group', '=', 'TIPO_MONEDA')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'TIPO_MONEDA')],limit=1))
