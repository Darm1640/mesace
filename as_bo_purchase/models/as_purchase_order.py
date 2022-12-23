from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import ValuationReconciliationTestCommon
from odoo.tests import Form, tagged
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def button_return_compra(self):
                #facturada
        cont=0
        imediate_obj=self.env['stock.immediate.transfer']
        #devorlver productos a inventario
        if self.picking_ids:
            # if len(self.picking_ids)==1:
            return_pick = False
            copy_picking = self.env['stock.picking']
            for picking_id in self.picking_ids:
                copy_picking |= picking_id
            for line in self.picking_ids:
                if line.state=='assigned': 
                    line.action_cancel()
            for picking_id in self.picking_ids:
                if picking_id.state=='cancel':
                    continue
                if picking_id.state=='done':
                    StockReturnPicking = self.env['stock.return.picking']
                    for move_line in picking_id.move_line_ids_without_package:
                        ventas = ''
                        cancelar_picking = self.env['stock.quant'].search([('lot_id','=',move_line.lot_id.id),('product_id','=',move_line.product_id.id),('location_id','=',move_line.location_dest_id.id)],order=" id desc",limit=1)
                        if cancelar_picking.quantity < move_line.qty_done:
                            move_pendientes = self.env['stock.move.line'].search([('lot_id','=',move_line.lot_id.id),('picking_id','!=',picking_id.id),('state','=','done')])
                            for moves in move_pendientes:
                                ventas += moves.picking_id.origin+','
                                raise UserError(_('los movimientos de origen %s deben devolver el stock del lote %s') % (ventas,str(move_line.lot_id.name)))

                    stock_return_picking_form = Form(self.env['stock.return.picking']
                        .with_context(active_ids=picking_id.ids, active_id=picking_id.ids[0],
                        active_model='stock.picking'))
                    stock_return_picking = stock_return_picking_form.save()
                    cont =0
                    # for move_line in picking_id.move_line_ids:
                    #     stock_return_picking.product_return_moves[cont].quantity = move_line.qty_done
                    #     cont += 1

                    res = stock_return_picking.create_returns()
                    return_pick = self.env['stock.picking'].browse(res['res_id'])
                    # for move_line in return_pick.move_line_ids:
                    #     for lot_line in lotes:
                    #         if move_line.product_id.id == lot_line['product_id']:
                    #             move_line.update({'lot_id':lot_line['lot_id']})
                    #     move_line.qty_done= move_line.product_qty

                    return_pick.action_assign()
                    wiz_act = return_pick.button_validate()
                    if wiz_act != True:
                        wiz = Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
                        wiz.process()
            for pick in copy_picking:
                pick.copy()
                    