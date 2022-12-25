# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit='sale.order'

    custom_customer_comment = fields.Text(
    	string="Customer Comment",
    	copy=False,
    	)