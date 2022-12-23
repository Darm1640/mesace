# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class as_res_partner(models.Model):
    _inherit = 'res.partner'

    as_tasas = fields.Float(string='Tasas ', default=0.0)