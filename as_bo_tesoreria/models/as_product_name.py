# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)

class AsProductName(models.Model):
    _name = 'as.product.name'

    name = fields.Char('Nombre')
    as_taxes_id = fields.Many2many('account.tax', string="Impuestos", default=lambda self: self.env.user.company_id.account_purchase_tax_id)
    as_account_gasto_id = fields.Many2one('account.account', string="Cuenta de Gasto")
