# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.tools import formatLang
from odoo.exceptions import UserError
from odoo import api, fields, models, _

class SaleBillUnion(models.Model):
    _inherit = 'as.sale.invoice.auto'

    def name_get(self):
        result = []
        for doc in self:
            name = doc.name or ''
            if doc.reference:
                name += ' - ' + doc.reference
            amount = doc.amount
            # if doc.sale_order_id and doc.sale_order_id.invoice_status == 'no':
            #     amount = 0.0
            name += ': ' + formatLang(self.env, amount, monetary=True, currency_obj=doc.currency_id)
            if doc.sale_order_id:
                name += ' - ' + doc.sale_order_id.as_template_id.name
            result.append((doc.id, name))
        return result

class SaleOrderCampos_aux(models.Model):
    _inherit = 'sale.order' 
    
    def action_draft(self):
        if any(order.state == 'cancel' and any(line.subscription_id and line.subscription_id.stage_id.category != 'in_progress' for line in order.order_line) for order in self):
            self.state = 'draft'
        return super(SaleOrderCampos_aux, self).action_draft()