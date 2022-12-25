# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError

class InvCreateWiard(models.Model):
    _name = 'inv.create.wizard.pro'
    
    date = fields.Date("Invoice Date")
    group_by_commission_type = fields.Boolean("Group By (Commission Type)")
    
    def create_inv(self):
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        analysis_obj = self.env['sale.commission.analysis']
        invoice_list = []
      
        check_invoice_created = analysis_obj.search([('id','in',self.env.context.get('active_ids',False)),('is_invoice','=',False)])
        if not check_invoice_created:
            raise UserError("Invoice Already Created.")
        
        for commission in  self.env.context.get('active_ids',False):
            commision_analysis = analysis_obj.browse(commission)
            
            sales_person = commision_analysis.sales_person_id
            commision_type = commision_analysis.type
            if self.group_by_commission_type:
                analysis_data = analysis_obj.search([('type','=',commision_type),('id','in',self.env.context.get('active_ids',False)),('is_invoice','=',False),('sales_person_id','=',sales_person.id)])
            else:
                analysis_data = analysis_obj.search([('id','in',self.env.context.get('active_ids',False)),('is_invoice','=',False),('sales_person_id','=',sales_person.id)])
           
            if analysis_data:
                inv_vals = {}
                inv_vals.update({'move_type' : 'in_invoice','partner_id':sales_person.partner_id.id,'invoice_date':self.date})
                domain = [
                    ('type', '=', 'purchase'),
                    ('company_id', '=', self.env.user.company_id.id),
                ]
                journal_id = self.env['account.journal'].search(domain, limit=1)
                inv_vals.update({'journal_id':journal_id.id})
                created_inv = inv_obj.create(inv_vals) 
                invoice_list.append(created_inv.id)
                invoice_line_ids = []
                for data in analysis_data:
                    
                    vals = {}
                    commission_product = self.env['product.product'].search([('type','=','service'),('name','ilike','Commission')],limit=1)
                    if not commission_product:
                        commission_product = self.env['product.product'].create({'name':'Sales Commission',
                                                            'type':'service'})
                    vals.update({'product_id' : commission_product.id})
                    vals.update({'name' : data.name})
                    accounts = commission_product.product_tmpl_id.get_product_accounts(created_inv.fiscal_position_id)
                    account = False
                   
                    account = accounts['expense']
                    if account == False:
                        raise UserError(_("No account defined for this product: " + commission_product.name))                                    
                    else:
                        vals.update({'account_id' : account.id})
                    
                    
                    vals.update({'quantity' : 1 ,'product_uom_id' : commission_product.uom_po_id.id,'price_unit':data.amount ,
                                 'move_id':created_inv.id,
                                 'tax_ids' : [(6, 0, commission_product.supplier_taxes_id.ids)]})    
                        
                    invoice_line_ids.append((0,0,vals))
                    
#                     created_inv_line = inv_line_obj.create(vals)
                    created_inv.write({'invoice_line_ids':invoice_line_ids}) 
                    created_inv._onchange_partner_id()
                    created_inv._onchange_invoice_line_ids()
                    data.write({'is_invoice':True})
         
        view = self.env.ref('account.view_invoice_tree')
        form_view = self.env.ref('account.view_move_form')
        return {
            "name":"Vendor Bill",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            'views': [(view.id, 'tree'),(form_view.id, 'form')],
            'view_id': view.id,
             "domain": [["id", "in", invoice_list]],
            "target": "current",                    
                }                

           
#        