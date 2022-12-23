# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "account.journal"

    as_type_journal = fields.Selection([('inbound', 'Ingreso'), ('outbound', 'Egreso'),('transfer','Transferencia')], string="Tipo de Diarios")
    as_anticipo = fields.Boolean(string='Es Diario Anticipo')
    as_fiscal = fields.Boolean('Es Fiscal', default=False)
    as_is_pago_anticipo = fields.Boolean('Es pago Contra anticipo', default=False)
    as_itf = fields.Many2one('account.account','Cuenta ITF')
    as_account_eg_positiva = fields.Many2one('account.account','Cuenta Diferencia Positiva (E) Egreso',domain="[('as_is_movimiento', '=', True)]")
    as_account_eg_negativo = fields.Many2one('account.account','Cuenta Diferencia Negativo (E) Egreso',domain="[('as_is_movimiento', '=', True)]")
    as_account_in_positivo = fields.Many2one('account.account','Cuenta Diferencia Positiva (I) Ingreso',domain="[('as_is_movimiento', '=', True)]")
    as_account_in_negativo = fields.Many2one('account.account','Cuenta Diferencia Negativo (I) Ingreso',domain="[('as_is_movimiento', '=', True)]")

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    _rec_name = 'name'
    _description = 'Bank Accounts'
    _order = 'sequence, id'

    name = fields.Char(string='Titulo')

    @api.onchange('acc_number','bank_id')
    def get_title(self):
        for bank in self:
            bank.name = str(bank.bank_id.name)+'-'+str(bank.acc_number)
