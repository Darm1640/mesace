# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError

import logging
_logger = logging.getLogger(__name__)

# Heredar el modelo de clientes y agregarle los campos adicionales
class res_users(models.Model):
    _inherit = 'res.users'

    as_sequence_id = fields.Many2one('ir.sequence', string='Secuencia para Ventas')

