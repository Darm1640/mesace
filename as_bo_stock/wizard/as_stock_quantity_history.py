# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#from odoo import api, fields, models


# class StockQuantityHistory(models.TransientModel):
#     _inherit = 'stock.quantity.history'
#     _description = 'Stock Quantity History inherit'

#     compute_at_date = fields.Selection([
#         (0, 'Current Inventory'),
#         (1, 'At a Specific Date'),
#         (2, 'Bajo Stock')
#     ], string="Compute", help="Choose to analyze the current inventory or from a specific date in the past.")

#     def open_table(self):
#         self.ensure_one()

#         if self.compute_at_date:
#             if str(self.compute_at_date != 2):
#                 tree_view_id = self.env.ref('stock.view_stock_product_tree').id
#                 form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
#                 # We pass `to_date` in the context so that `qty_available` will be computed across
#                 # moves until date.
#                 action = {
#                     'type': 'ir.actions.act_window',
#                     'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
#                     'view_mode': 'tree,form',
#                     'name': _('Products'),
#                     'res_model': 'product.product',
#                     'domain': "[('type', '=', 'product')]",
#                     'context': dict(self.env.context, to_date=self.date),
#                 }
#                 return action
#             else:
#                 tree_view_id = self.env.ref('stock.view_stock_quant_tree').id
#                 #form_view_id = self.env.ref('stock.product_form_view_procurement_button').id, (form_view_id, 'form')
#                 # We pass `to_date` in the context so that `qty_available` will be computed across
#                 # moves until date.

#                 action = {
#                     'type': 'ir.actions.act_window',
#                     'views': [(tree_view_id, 'tree')],
#                     'view_mode': 'tree',
#                     'name': _('Products'),
#                     'res_model': 'stock.quant',
#                     'domain': self.compute_low_stock(),
#                     'context': dict(self.env.context),
#                 }
#                 return action
#         else:
#             self.env['stock.quant']._merge_quants()
#             self.env['stock.quant']._unlink_zero_quants()
#             vista = self.env.ref('stock.quantsact')
#             vista.domain="[]"
#             return vista.read()[0]


#     def compute_low_stock(self):
#         product_quant = self.env['stock.quant'].sudo().search([])
#         bajo_stock=[]
#         for quant in product_quant:
#             if quant.location_id.usage =='internal':
#                 stock_min = quant.product_id.product_tmpl_id.as_qty_min + quant.product_id.product_tmpl_id.as_qty_security
#                 if quant.quantity <= stock_min:
#                     bajo_stock.append(quant.id)
#         return "[('id','in',"+str(tuple(bajo_stock))+")]"