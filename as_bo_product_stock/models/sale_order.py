# -*- coding: utf-8 -*-

from odoo import api, models


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.onchange('user_id')
    def onchange_user_id(self):
        """
        Onchange method for user_id

        Attr update:
         * warehouse_id - as default user warehouse
        """
        for order in self:
            if order.user_id and order.user_id.default_warehouse:
                order.warehouse_id = order.user_id.default_warehouse
