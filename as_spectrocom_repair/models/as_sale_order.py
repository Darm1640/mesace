# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class as_sale_order(models.Model):
    _inherit = 'sale.order'

    as_repair_id = fields.Many2one('repair.order',string="Reparación")
    as_repair_sheet_id = fields.Many2one('as.repair.order.sheet',string="Reparación")

class as_sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    as_repair_id = fields.Many2one('repair.order',string="Reparación")