# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AsStockImmediateTransfer(models.TransientModel):
    """Heredado modelo para hacer positivo el costo"""
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'

    def process(self):
        result = super(AsStockImmediateTransfer,self).process()
        # for picking in self.pick_ids:
        #     for move in picking.move_lines:
        #         if move._is_out():
        #             price_unit = move.location_id.with_context(product_id=[move.product_id.id]).price_unit
        #             move.write({
        #                 'price_unit': price_unit,
        #             })
        return result