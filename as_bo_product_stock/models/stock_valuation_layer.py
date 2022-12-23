# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = 'stock.valuation.layer'
    _description = 'Stock Valuation Layer inherit'

    location_id = fields.Many2one('stock.location', 'Ubicación', readonly=True)


class AsProductValuaction(models.Model):
    """Modelo que guarda los costos por ubicacion"""

    _name = 'as.valuation.location'
    _description = 'Modelo que guarda los costos por ubicacion'

    product_id = fields.Many2one('product.product', 'Producto')
    location_id = fields.Many2one('stock.location', 'Ubicación')
    unit_cost = fields.Float('Costo')

    _sql_constraints = [
        ('name_location_product_uniq', 'unique(product_id,location_id)', 'Producto y ubicacion deben ser unicos!'),
    ]