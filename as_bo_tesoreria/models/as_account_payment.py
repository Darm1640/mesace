# -*- coding: utf-8 -*-
from lxml import etree
from dateutil.relativedelta import relativedelta
from odoo import api, exceptions, fields, models, _
import logging
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class AsAccountPayment(models.Model):
    _inherit = "account.payment"

    as_is_anticipo = fields.Boolean(string="Es Anticipo", help=u'Registrar Pago tipo Antipo.',default=False)
    payment_acquirer_id = fields.Many2one('as.payment.acquirer', string='Método de Pago')
    as_numero_documento = fields.Char('Nro documento', help=u'Número del documento del banco.')
    

    