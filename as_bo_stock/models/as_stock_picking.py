from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import uuid

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    as_worker_signature = fields.Binary(string='Firma del Trabajor')
    as_customer_signature = fields.Binary(string='Firma del Cliente')
    as_asiento_count = fields.Integer(compute="_invoice_count")

    def action_assign(self):
        for move in self.move_ids_without_package:
            filtro = ''
            if move.product_id:
                filtro+='product_id = '+str(move.product_id.id)+' and '
            if move.location_id:
                filtro+='location_id = '+str(move.location_id.id)
            query_movements = ("""
                SELECT id from stock_quant
                WHERE
                 """+str(filtro)+""" 
            """)
            self.env.cr.execute(query_movements)
            all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
            for line in all_movimientos_almacen:
                query_movements = (""" UPDATE stock_quant SET reserved_quantity=0 WHERE id = """+str(line[0])+""" """)
                self.env.cr.execute(query_movements)
        res = super(StockPicking, self).action_assign()
        return res

    def do_unreserve(self):
        res = super(StockPicking, self).do_unreserve()
        for move in self.move_ids_without_package:
            filtro = ''
            if move.product_id:
                filtro+='product_id = '+str(move.product_id.id)+' and '
            if move.location_id:
                filtro+='location_id = '+str(move.location_id.id)
            query_movements = ("""
                SELECT id from stock_quant
                WHERE
                 """+str(filtro)+""" 
            """)
            self.env.cr.execute(query_movements)
            all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
            for line in all_movimientos_almacen:
                query_movements = (""" UPDATE stock_quant SET reserved_quantity=0 WHERE id = """+str(line[0])+""" """)
                self.env.cr.execute(query_movements)
        if len(self.move_line_ids_without_package) > 1:
            self.move_line_ids_without_package.unlink()

        return res

    def _invoice_count(self):
        for rec in self:
            rec.ensure_one()
            account_picking_line = self.env['stock.move.line'].search([
                ('picking_id', '=', rec.id),
            ])
            account_asiento_line = self.env['account.move'].search([
                ('stock_move_id', '=', account_picking_line.move_id.ids),
            ])
            rec.as_asiento_count = len(account_asiento_line.mapped('id'))

    def action_view_asiento(self):
        self.ensure_one()
        action_pickings = self.env.ref('account.action_move_journal_line')
        action = action_pickings.read()[0]
        action['context'] = {}
        account_picking_line = self.env['stock.move.line'].search([
                ('picking_id', '=', self.id),
            ])
        account_asiento_line = self.env['account.move'].search([
            ('stock_move_id', '=', account_picking_line.move_id.ids),
        ])
        action['domain'] = [('id', 'in', account_asiento_line.ids)]
        return action
    
    
    def action_update_realizado(self):
        for pick in self:
            #productos sin seguimiento
            for move_line in pick.move_line_ids_without_package:
                if move_line.product_id.tracking == 'none':
                    move_line.qty_done = move_line.product_uom_qty
                    mensaje = '<b style="color:blue">Producto: '+str(move_line.product_id.name)+'cantidad: '+str(move_line.qty_done)+'</b>'
                    self.message_post(body = str(mensaje), content_subtype='html')  
            #productos con seguimiento por serie
            move_lines_commands = []
            if pick.picking_type_id.use_create_lots and not pick.picking_type_id.use_existing_lots:
                for move in pick.move_ids_without_package:
                    prefijo = uuid.uuid4().hex[:3]
                    count = 1
                    if move.product_id.tracking == 'serial':
                        if move.move_line_ids:
                            for line_move in move.move_line_ids:
                                lot_name = self.as_get_lot_name(count,prefijo,move)
                                line_move.lot_name = lot_name
                                line_move.qty_done = 1
                                count += 1
                        else:
                            for i in range(1,move.product_uom_qty):
                                lot_name = self.as_get_lot_name(count,prefijo,move)
                                move_lines_commands.append((0, 0, {
                                    'lot_name': lot_name,
                                    'qty_done': 1,
                                    'product_id': move.product_id.id,
                                    'product_uom_id': move.product_id.uom_id.id,
                                    'location_id': move.location_id.id,
                                    'location_dest_id': move.location_dest_id.id,
                                    'picking_id': move.picking_id.id,
                                }))
                                count += 1
                            move.write({'move_line_ids': move_lines_commands})

    def as_get_lot_name(self,cont,prefijo,product_id):
        lot_name = ''
        lot_name = str(prefijo)+str(product_id.id)+'-'+str(cont)
        return lot_name
    

class Asstockpickingtype(models.Model):
    _inherit = "stock.picking.type"
    _description = "Packages type"

    as_extract_cost = fields.Boolean(string='Extraer Costo de Origen de producto',default=False)


class StockMove(models.Model):
    _inherit = "stock.move"
    
    @api.onchange('product_id')
    def get_price_unit(self):
        for line in self:
            costo = 0.0
            if line.picking_id.picking_type_id.as_extract_cost:
                if line.price_unit <= 0.0:
                    costo= self.env['stock.valuation.layer'].sudo().search([('product_id','=',line.product_id.id),('location_id','=',line.picking_id.location_id.id),('unit_cost','>',0.0)],order='create_date desc',limit=1).unit_cost
                    if costo <= 0.0:
                        costo = line.product_id.standard_price
                    line.price_unit = costo


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        res = super(ReturnPicking, self).create_returns()
        picking_id = self.env['stock.picking'].browse(res['res_id'])
        for move in picking_id.move_ids_without_package:
            move.get_price_unit()
        return res
    
    def _create_returns(self):
        a=0
        res = super(ReturnPicking, self)._create_returns()
        picking_id = self.env['stock.picking'].browse(res[0])
        if picking_id:
            picking_id.origin = 'DEVOLUCION DE ' + str(picking_id.name)
        return res
        

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('product_id')
    def get_unidad_line(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    @api.depends('product_id')
    def get_unidad_line2(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    @api.model_create_multi
    def create(self, values):
        res = super(StockMoveLine, self).create(values)
        for line in res:
            line.move_id.get_price_unit()
        return res