# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError

import logging
_logger = logging.getLogger(__name__)

# Heredar el modelo de clientes y agregarle los campos adicionales
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    as_nit_ids = fields.One2many('as.nits', 'partner_id', string="Nits Asociados")