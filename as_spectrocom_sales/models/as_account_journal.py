# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "account.journal"

    as_is_v_autorizada = fields.Boolean('Es diario de Venta autorizada', default=False)