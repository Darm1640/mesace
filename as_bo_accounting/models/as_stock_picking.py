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

class AccountMove(models.Model):
    _inherit = "stock.picking"

    as_glosa = fields.Char(string="Glosa auxiliar")

    def button_validate(self):
        res = super().button_validate()
        self.as_glosa = self.name + ' - ' + self.origin
        return res