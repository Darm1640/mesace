# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo.tools.float_utils import float_round, float_is_zero
from datetime import datetime
from dateutil import relativedelta
from werkzeug.urls import url_encode
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def as_subtotal_converter(self,cant):
        valor = 0.0
        for line in self:
            price = line.price_unit * cant
            monto_discount = (price*line.discount)/100
            valor = line.currency_id._convert(price+monto_discount, self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today(), round=False)
        return valor
