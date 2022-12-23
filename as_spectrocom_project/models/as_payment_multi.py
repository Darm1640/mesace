# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, SU, SA
_logger = logging.getLogger(__name__)


class AsPaymentMulti(models.Model):
    _inherit = 'as.payment.multi'

    as_project_id = fields.Many2one('project.task', string="Proyecto")
    as_is_negativo = fields.Boolean(string="Es diferencia negativa")


