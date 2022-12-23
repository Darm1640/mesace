# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError
import re
import xlrd
from xlrd import open_workbook
import base64
import logging
_logger = logging.getLogger(__name__)

class as_importar_productos(models.Model):
    _name="as.actualizador.costos.wizard"
    _description="Actualizador de costos de productos"

    def actualizar_costos_productos(self):
        self.ensure_one()
        context = self._context
        product_template_ids = self.env[context['active_model']].search([('id','in',tuple(self._context['active_ids']))])
        for product in product_template_ids:
            product.action_updates_cost()