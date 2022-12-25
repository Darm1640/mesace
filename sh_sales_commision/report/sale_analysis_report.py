# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError


class SaleCommissionAnalysisReportData(models.AbstractModel):
    _name = 'report.sh_sales_commision.report_sales_commission'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        
        sale_commission_obj = self.env["sale.commission.analysis"]
        order_list = []
             
        if data.get('user_id',False):
            order_list = []
            order_dic = {}
            domain = [
                ('date','>=',data['start_date']),('date','<=',data['end_date']),('sales_person_id','=',data['user_id'])
                ]
            search_orders = sale_commission_obj.search(domain)
            if search_orders:
                
                for commission in search_orders:
                    order_dic = {'name':commission.name,
                    'date':commission.date,
                    'commission_name':commission.commission_name.name,
                    'product_id':commission.product_id.name,
                    'partner_id':commission.partner_id.name,
                    'amount':commission.amount}
             
                    if commission.order_id:
                        order_dic.update({'order_ref':commission.order_id.name})
                    if commission.move_id:
                        order_dic.update({'order_ref':commission.move_id.name})
                         
                    if commission.type=='standard':
                        order_dic.update({'commission_type':'Standard'})
                    elif commission.type == 'partner':
                        order_dic.update({'commission_type':'Partner Based'})
                    elif commission.type == 'product':
                        order_dic.update({'commission_type':'Product/ Product Category/ Margin Based'})
                    elif commission.type == 'discount':
                        order_dic.update({'commission_type':'Discount Based'})
                    order_list.append(order_dic)

        data =  {
            'date_start': data['start_date'],
            'date_end': data['end_date'],
            'name_user':data['user_name'],
            'order_list':order_list
        }        
        return data

    
class SaleCommissionAnalysisReport(models.Model):
    _name = 'sale.commission.analysis.report'
    
    start_date = fields.Date("Start Date",dafault=fields.Date.today())
    end_date = fields.Date("End Date",dafault=fields.Date.today())
    user_id = fields.Many2one("res.users",string="Sales Person")
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.end_date and c.start_date > c.end_date):
            raise ValidationError(_('start date must be less than end date.'))    
        
    def print_report(self):
        datas = self.read()[0]

        datas = datas or {}
        
        datas.update({
            "user_name": self.user_id.name,
            "user_id":self.user_id.id
            })
        
        return self.env.ref('sh_sales_commision.action_report_sales_commission').report_action([], data = datas)    