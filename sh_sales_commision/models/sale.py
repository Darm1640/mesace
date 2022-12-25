# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def check_show_commission(self):
        for rec in self:
            if rec.company_id.commission_based_on_so:
                rec.show_commission = True
            else:
                rec.show_commission = False
    
    sales_commission_ids = fields.One2many('sale.commission.analysis','order_id',string="Sales Commission")
    show_commission = fields.Boolean(compute='check_show_commission',string="Show Commission")

    def create_commision(self, analysis_vals):
        sale_commission_analysis = self.env['sale.commission.analysis']
        analysis_vals.update({'date':fields.Date.today(),
                                 'sales_person_id':self.user_id.id,
                                 'order_ref':self.name,
                                 'order_id':self.id,
                                 
                                 })
        sale_commission_analysis.create(analysis_vals)
                
    def action_confirm(self):
        if self.env.user.company_id.commission_based_on_so:
            sale_commission = self.env['sale.commission']
            analysis_vals = {}
            related_sale_commissions = sale_commission.search([('user_ids.id','=',self.user_id.id)])
            if related_sale_commissions:
                for related_sale_commission in related_sale_commissions:
                    commission_per = 0.0
                    commission_amount = 0.0
                    if related_sale_commission.type == 'standard':
                        analysis_vals.update({'type':'standard','commission_name':related_sale_commission.id})
                        commission_per = related_sale_commission.standard_commission_per
                        if commission_per >0.0:
                            commission_amount = self.amount_untaxed * (commission_per/100)
                            analysis_vals.update({'amount':commission_amount,
                                                  'name':related_sale_commission.type +' * '+ related_sale_commission.name + ' ( '+ str(commission_per) +' % )'})
                            
                            self.create_commision(analysis_vals)
                            analysis_vals = {}
                    elif related_sale_commission.type == 'partner':
                        analysis_vals.update({'type':'partner','commission_name':related_sale_commission.id})
                        if self.partner_id and self.partner_id.affiliated:
                            commission_per = related_sale_commission.affiliated_commission_per
                            analysis_vals.update({'partner_type':'Affiliated'})
                        else:
                            commission_per = related_sale_commission.non_affiliated_commission_per
                            analysis_vals.update({'partner_type':'Non-Affiliated'})
                        if commission_per >0.0:
                            commission_amount = self.amount_untaxed * (commission_per/100)
                            analysis_vals.update({'amount':commission_amount,
                                                  'partner_id':self.partner_id.id,
                                                  'name':related_sale_commission.type +' * '+ related_sale_commission.name + ' ( '+ str(commission_per) +' % )'})
                            
                        self.create_commision(analysis_vals)
                        analysis_vals = {}
                            
                    elif related_sale_commission.type == 'product':
                        
                        if related_sale_commission.product_commission_lines:
                            for line in related_sale_commission.product_commission_lines:
                                analysis_vals.update({'type':'product','commission_name':related_sale_commission.id})
                                
                                if line.with_commission == 'fix':
                                    if line.based_on =='product' and line.product_id and self.order_line.filtered(lambda x:x.product_id==line.product_id):
                                        commission_per = 0.0
                                        commission_amount =0.0
                                        for order_line in self.order_line.filtered(lambda x:x.product_id==line.product_id):
                                            if order_line.price_unit>0.0:
                                                product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                    
                                                if line.target_price < product_price_diff:
                                                    commission_per = line.above_price_commission
                                                    
                                                    commission_amount += (product_price_diff-line.target_price)*(commission_per/100)
                                                    
                                                    analysis_vals.update({'amount':commission_amount,
                                                      'product_id':order_line.product_id.id,
                                                      'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                      +' for Product '+ order_line.product_id.name})
                                                    
                                        self.create_commision(analysis_vals)
                                        analysis_vals = {}
                                    elif line.based_on =='categories' and line.category_id and self.order_line.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                        commission_per = 0.0
                                        commission_amount =0.0
                                        for order_line in self.order_line.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                            if order_line.price_unit>0.0:
                                                product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                    
                                                if line.target_price < product_price_diff:
                                                    commission_per = line.above_price_commission
                                                    commission_amount += (product_price_diff-line.target_price)*(commission_per/100)
                                                    analysis_vals.update({'amount':commission_amount,
                                                                          'category_id':line.category_id.id,
                                                      'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                      +' for Product '+ order_line.product_id.name})
                                        self.create_commision(analysis_vals)
                                        analysis_vals = {}
                                elif line.with_commission == 'margin':
                                    if line.based_on =='product' and line.product_id and self.order_line.filtered(lambda x:x.product_id==line.product_id):
                                        commission_per = 0.0
                                        commission_amount =0.0
                                        for order_line in self.order_line.filtered(lambda x:x.product_id==line.product_id):
                                            if order_line.price_unit>0.0:
                                                product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                if product_price_diff >0.0:
                                                    product_margin = (100*product_price_diff)/(order_line.price_unit)
                                                    
                                                    if product_margin > line.target_margin:
                                                        commission_per = line.above_margin_commission
                                                    else:
                                                        commission_per = line.below_margin_commission
                                                        
                                            
                                                    if commission_per >0.0:
                                                        commission_amount += product_price_diff*(commission_per/100)
                                                        analysis_vals.update({'amount':commission_amount,
                                                           'product_id':order_line.product_id.id,
                                                          'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                          +' for Product '+ order_line.product_id.name}) 
                                        self.create_commision(analysis_vals)
                                        analysis_vals = {}
                                    elif line.based_on =='categories' and line.category_id and self.order_line.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                        commission_per = 0.0
                                        commission_amount =0.0
                                        for order_line in self.order_line.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                            if order_line.price_unit>0.0:
                                                product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                if product_price_diff >0.0:
                                                    product_margin = (100*product_price_diff)/(order_line.price_unit)
                                                    
                                                    if product_margin > line.target_margin:
                                                        commission_per = line.above_margin_commission
                                                    else:
                                                        commission_per = line.below_margin_commission
                                                        
                                            
                                                    if commission_per >0.0:
                                                        commission_amount += product_price_diff*(commission_per/100)
                                                        analysis_vals.update({'amount':commission_amount,
                                                                              'category_id':line.category_id.id,
                                                          'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                          +' for Product '+ order_line.product_id.name})  
                                
                                        self.create_commision(analysis_vals)
                                        analysis_vals = {}
                                elif line.with_commission == 'exception':
                                    if line.based_on =='product' and line.product_id and self.order_line.filtered(lambda x:x.product_id==line.product_id):
                                        commission_per = 0.0
                                        commission_amount =0.0
                                        for order_line in self.order_line.filtered(lambda x:x.product_id==line.product_id):
                                            if order_line.price_unit>0.0:
                                                product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                commission_per = line.exception_commission
                                                    
                                        
                                                if commission_per >0.0 and product_price_diff>0.0:
                                                    commission_amount += product_price_diff*(commission_per/100)
                                                    analysis_vals.update({'amount':commission_amount,
                                                                          'product_id':order_line.product_id.id,
                                                      'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                      +' for Product '+ order_line.product_id.name})  
                                        self.create_commision(analysis_vals)
                                        analysis_vals = {}
                                    elif line.based_on =='categories' and line.category_id and self.order_line.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                        commission_per = 0.0
                                        commission_amount =0.0
                                        for order_line in self.order_line.filtered(lambda x:x.product_id.categ_id==line.category_id):
                                            if order_line.price_unit>0.0:
                                                product_price_diff = (order_line.price_unit)-(order_line.product_id.standard_price)
                                                commission_per = line.exception_commission
                                        
                                                if commission_per >0.0 and product_price_diff>0.0:
                                                    commission_amount += product_price_diff*(commission_per/100)
                                                    analysis_vals.update({'amount':commission_amount,
                                                                          'category_id':line.category_id.id,
                                                      'name':related_sale_commission.name + ' ( '+ str(commission_per) +' % )'
                                                      +' for Product '+ order_line.product_id.name})  
                   
                                        self.create_commision(analysis_vals)
                                        analysis_vals = {}
                    
       
        return super(SaleOrder, self).action_confirm()