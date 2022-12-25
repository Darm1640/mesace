# -*- coding: utf-8 -*-

from odoo import fields, models,api,_

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        for rec in res.order_line:
            if not rec.display_type:
                rec.sequence = rec.product_id.sequence
            else:
                rec.sequence = 1000
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for rec in self.order_line:
            if not rec.display_type:
                rec.sequence = rec.product_id.sequence
            else:
                rec.sequence = 1000
        return res