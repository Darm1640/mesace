# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
#Generacion del QR
import qrcode
import tempfile
import base64
#Convertir numeros en texto
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time
from time import mktime
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
class asPurchase(models.Model):
    _inherit = 'purchase.order'

    as_import_fiscal = fields.Boolean(string="Import Fiscal")
    as_landed_uno = fields.Many2one('stock.landed.cost', 'Land Uno')
    as_landed_dos = fields.Many2one('stock.landed.cost', 'Land Dos')
