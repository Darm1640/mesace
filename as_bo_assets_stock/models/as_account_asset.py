# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.asset.asset'

    as_picking_id = fields.Many2one('stock.picking', string='Movimiento', states={'draft': [('readonly', False)]}, copy=False)
    as_move_id = fields.Many2one('stock.move.line', string='Movimiento Linea', states={'draft': [('readonly', False)]}, copy=False)
    as_code_assets = fields.Char(string='Código Activo')
    as_lot_id = fields.Many2one('stock.production.lot', string='Nro. Serie/Lote',copy=False)
    as_value = fields.Float(string='Valor asignado')
    as_sale = fields.Many2one('sale.order', string='Venta')