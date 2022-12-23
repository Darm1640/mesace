# -*- coding: utf-8 -*-
from datetime import datetime
from email.policy import default
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, ormcache
import logging
import json

import datetime
from datetime import datetime, timedelta, date
from time import mktime
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit="hr.payslip"

    def action_payslip_cancel(self):
        # CONDICION COMENTADA PARA PODER CANCELAR NOMINAS EN ESTADO HECHO
        # if self.filtered(lambda slip: slip.state == 'done'):
        #     raise UserError(_("Cannot cancel a payslip that is done."))
        self.write({'state': 'cancel'})
        self.mapped('payslip_run_id').action_close()