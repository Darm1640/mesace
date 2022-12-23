# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError
import json 


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    # def button_cancel(self):
    #     for order in self:
    #         if order.picking_ids:
    #             for picking in order.picking_ids:
    #                 for move_line in picking.move_line_ids_without_package:
    #                     if move_line.product_id.tracking != 'none':
    #                         if not self.as_get_history_lot(move_line.lot_id,move_line.id):
    #                             move_line.lot_id.active= False

               
    #     res = super(purchase_order, self).button_cancel()
    #     return res

    # def as_get_history_lot(self,lot,iid):
    #     moves_line = self.env['stock.move.line'].sudo().search([('id','!=',iid),('lot_id','=',lot.id),('state','=','done')])
    #     if moves_line:
    #         name = ''
    #         for lot in moves_line:
    #             if not lot.picking_id.name:
    #                 pass
    #             else:
    #                 name+=lot.picking_id.name+', '
                

    #         raise UserError(_('Debe cancelar estos movimeintos %s') % (name))
    #     else:
    #         return False