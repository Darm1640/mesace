# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api

class Partner(models.Model):
    _inherit = 'res.partner'

    affiliated = fields.Boolean("Affiliated")
    
class SaleCommission(models.Model):
    _name = 'sale.commission'
    
    name = fields.Char("Commission Name")
    user_ids = fields.Many2many('res.users',string="Sales Person")
    type = fields.Selection([('standard','Standard'),('partner','Partner Based'),
                             ('product','Product/ Product Category/ Margin Based')],string="Commission Type")
    
    standard_commission_per = fields.Float("Standard Commission Percentage")
    affiliated_commission_per = fields.Float("Affiliated Partner Commission Percentage")
    non_affiliated_commission_per = fields.Float("Non-Affiliated Partner Commission Percentage")
    
    product_commission_lines = fields.One2many('product.commission.line','commission_id',string="Product Commission Line")
    
class CommissionLine(models.Model):
    _name = 'product.commission.line'
    
    
    commission_id = fields.Many2one('sale.commission',string="Commission")
    based_on = fields.Selection([('product','Product'),('categories','Product Categories')],string="Based on",default="product")
    
    with_commission = fields.Selection([('fix','Fix Price'),('margin','Margin'),
                                 ('exception','Commission Exception')],string="With",default="fix")
    
    product_id = fields.Many2one('product.product',string="Product")
    category_id=fields.Many2one('product.category',string="Product Category")
    
    target_price = fields.Float("Target Price")
    above_price_commission = fields.Float("Above Price Commission %")
    
    target_margin = fields.Float("Target Margin %")
    above_margin_commission = fields.Float("Above Margin Commission %")
    below_margin_commission = fields.Float("Below Margin Commission %")
    
    exception_commission = fields.Float("Commission %")
    
    
    
   
    