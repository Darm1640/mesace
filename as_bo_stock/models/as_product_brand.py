# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AsProductBrand(models.Model):
	_name = 'as.product.brand'
	_description = "Marca de Producto"
	_rec_name = 'as_name'

	as_name = fields.Char(string='Marca', required=True)
	as_description = fields.Char(string='Descripcion')