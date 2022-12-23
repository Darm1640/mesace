# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsTipoRetencion(models.Model):
    _inherit = 'as.tipo.retencion'

    as_gasto_fiscal = fields.Boolean(string="Gasto Fiscal")