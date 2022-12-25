# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

     
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    commission_based_on_so = fields.Boolean("Commission based on sales order",default=False)
    
    commission_based_on_invoice = fields.Boolean("Commission based on invoice",
                                             default=False)
    
    commission_based_on_payment = fields.Boolean("Commission based on payment",
                                             default=False)
    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    commission_based_on_so = fields.Boolean("Commission based on sales order",
                                             related='company_id.commission_based_on_so',readonly=False)
    
    commission_based_on_invoice = fields.Boolean("Commission based on invoice",
                                             related='company_id.commission_based_on_invoice',readonly=False)
    
    commission_based_on_payment = fields.Boolean("Commission based on payment",
                                             related='company_id.commission_based_on_payment',readonly=False)
    