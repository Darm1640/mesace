# -*- coding: utf-8 -*-

import time

import odoo
from odoo import api, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import psycopg2
from . import as_amount_to_text_es
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)
#clase heredada de purchase order para agregar funciones de creacion de facturas y campos adicionales
class as_account_invoice(models.Model):
    _inherit = 'account.move'
    