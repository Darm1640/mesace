# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    code = fields.Char(string="Identifier")
    description = fields.Char(string="Description")
    is_percent = fields.Boolean(string="Is percent", default=True)

class AccountGroup(models.Model):
    _inherit = "account.group"
    _parent_store = True
    _order = 'code_prefix'
    
    code_prefix = fields.Char()
    
    @api.onchange('name', 'code_prefix', 'code_prefix_start')
    def _onchange_code(self):
        if self.code_prefix:
            if self.code_prefix:
                self.code_prefix_start = self.code_prefix
                self.code_prefix_end = self.code_prefix
            else:
                self.code_prefix = self.code_prefix_start

class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    min_base = fields.Float(default=0, string="Base mínima")
    retefuente = fields.Boolean('Impuesto de Retefuente')
