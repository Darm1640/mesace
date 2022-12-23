from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'as.level.approval'

    as_type = fields.Selection(selection_add=[('in_invoice', 'Facturas de Proveedor')], ondelete={'in_invoice': 'cascade'})

