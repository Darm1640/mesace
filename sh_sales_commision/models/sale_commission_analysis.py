# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api

class SaleCommissionAnalysis(models.Model):
    _name = 'sale.commission.analysis'
    
    name = fields.Char("Description")
    date = fields.Date("Date")
    sales_person_id = fields.Many2one("res.users",string="Sales Person")
    invoice_ref = fields.Char("Invoice Reference")
    order_ref = fields.Char("Order Reference")
    type = fields.Selection([('standard','Standard'),('partner','Partner Based'),
                             ('product','Product/ Product Category/ Margin Based'),
                             ('discount','Discount Based')],string="Sales Commission")
    
    commission_name = fields.Many2one('sale.commission',string="Commission Name")
    product_id = fields.Many2one('product.product',string="Product")
    category_id=fields.Many2one('product.category',string="Product Category")
    sub_category_id=fields.Many2one('product.category',string="Product Sub-Category")
    partner_id = fields.Many2one('res.partner',string="Partner")
    partner_type = fields.Char("Partner Type")
    amount=fields.Float("Commission Amount")
    order_id = fields.Many2one('sale.order',string="Order Reference")
    move_id = fields.Many2one('account.move',string="Invoice Reference")
    is_invoice = fields.Boolean("Is Invoice")
        