# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import float_compare
from odoo.tools.misc import formatLang, format_date, get_lang
from dateutil import relativedelta
from odoo.exceptions import UserError, AccessError
from datetime import timedelta, datetime
import calendar
import time
from dateutil.relativedelta import relativedelta
import json
import logging
from collections import defaultdict
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    # as_glosa = fields.Char(string="Glosa auxiliar")

    # GLOSA
    # def _account_entry_move(self, qty, description, svl_id, cost):
    #     description = self.reference + ' ' + self.origin + ' ' #+ self.partner_id.name
    #     # res = super(StockMove, self)._account_entry_move(qty, description, svl_id, cost) crear un campo de tipo char en account move donde al validar la factura le asigne el valor a la relacion 
    #     res = super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
    #     # self.as_glosa = self.name + ' - ' + self.origin
    #     return res