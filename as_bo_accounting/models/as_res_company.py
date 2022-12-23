# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    as_is_movimiento = fields.Boolean(string="Es cuenta de Movimiento", default=False)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def create(self,vals):
        res = super(AccountMove, self).create(vals)
        for line in res.line_ids:
            if not line.account_id.as_is_movimiento:
                raise UserError(_('La cuenta  %s no es de movimiento')%line.account_id.name)
        return res

    # @api.multi
    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for line in self.line_ids:
            if not line.account_id.as_is_movimiento:
                raise UserError(_('La cuenta  %s no es de movimiento')%line.account_id.name)
        return res