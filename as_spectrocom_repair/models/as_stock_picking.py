# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class as_stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    as_repair_id = fields.Many2one('repair.order', 'Repair Order')

class as_stock_move(models.Model):
    _inherit = 'stock.move'
    
    as_repair_line = fields.Many2one('repair.line', 'Repair Order line')
    as_nota = fields.Char('Nota')