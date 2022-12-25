# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    can_not_see_cost = fields.Boolean(
        compute='compute_can_not_see_cost'
    )

    def compute_can_not_see_cost(self):
        for product in self:
            product.can_not_see_cost = self.env.user.has_group(
                'ats_custom_cost.group_no_margin_no_cost')