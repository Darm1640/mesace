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
class AccountInvoice(models.Model):
    _inherit = 'account.move'

    as_monto_excento = fields.Float(string="Monto Excento")
    as_numero_dui  = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.')
    as_numero_autorizacion_dui = fields.Char(string='No Autorizacion Dui', help='Numero de Autorizacion.', size=15, digits=(15, 0))
