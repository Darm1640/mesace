# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import date, time
from odoo.tools.safe_eval import safe_eval
import logging
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import math
#from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class AsStockProduct(models.Model):
    _name = 'as.stock.product'
    _description = 'Aprobe sale Wizard'

    sale_line_id = fields.Many2one('sale.order.line', 'Linea')
    product_id = fields.Many2one('product.product', 'Producto')
    default_code = fields.Char('Código', related="product_id.default_code")
    udm = fields.Many2one('uom.uom', string="UDM")
    udm_sale = fields.Many2one('uom.uom', string="UDM Venta")
    lines_ids = fields.Many2many('as.stock.product.line', string='Lineas de Productos')
    lines_stock_ids = fields.Many2many('as.stock.route.line', string='Stocks de Productos')
    stock = fields.Float(string="stock")

    @api.model
    def default_get(self, fields):
        res = super(AsStockProduct, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        dictline = []
        dictlinestock = []
        stock = 1
        menor = 0.0
        value = 0.0
        if res_ids and res_ids[0]:
            so_line = res_ids[0]
            so_line_obj = self.env['sale.order.line'].browse(so_line)
            route_ids = self.env['stock.location.route'].search([('sale_selectable','=',True)])
            for route in route_ids:
                as_lot_stock = ''
                lotes = []
                stock = 0.0
                location_id = self.env['stock.location'] #LocacionID
                for push in route.rule_ids:
                    if push.sequence == 1:
                        location_id = push.location_src_id.id
                if location_id:
                    if len(self.as_get_lotes_stock(so_line_obj.product_id.id,location_id)) > 0:
                        stock = self.as_get_lotes_stock(so_line_obj.product_id.id,location_id)[0][1]
                    if len(so_line_obj.product_id.bom_ids) > 0:
                        for bom in so_line_obj.product_id.bom_ids:
                            location = self.env['stock.location'].search([('id','=',location_id)])

                            if  len(bom.bom_line_ids) > 0:
                                if len(self.as_get_lotes_stock(bom.bom_line_ids[0].product_id.id,location_id)) > 0:
                                    stock = self.as_get_lotes_stock(bom.bom_line_ids[0].product_id.id,location_id)[0][1]
                                menor = stock/bom.bom_line_ids[0].product_qty
                            for bom_line in bom.bom_line_ids:
                                stock_bom = 0.0
                                lotes_row = self.as_get_lotes(bom_line.product_id.id,location_id)
                                lotes = []
                                locations = []
                                for lot in lotes_row:
                                    if len(lot) > 0:
                                        lotes.append(lot[1])
                                        locations.append(lot[0])
                                value = bom_line.product_qty
                                if len(self.as_get_lotes_stock(bom_line.product_id.id,location_id)) > 0:
                                    stock_bom = self.as_get_lotes_stock(bom_line.product_id.id,location_id)[0][1]
                                for lote in self.as_get_lotes_location(bom_line.product_id.id,location_id):
                                    lot_id = self.env['stock.production.lot'].search([('id','=',lote[0])])
                                    quant = self.env['stock.quant']
                                    stock_l = quant._get_available_quantity(so_line_obj.product_id,location,lot_id=lot_id)
                                    as_lot_stock +='['+lot_id.name+']-'+str(round(stock_l,2))+','
                                    lotes.append(lote[0])
                                qty = stock_bom/value
                                if  qty < menor:
                                    menor=  qty
                        stock = menor
                    else:
                        lotes = []
                        for lote in self.as_get_lotes_location(so_line_obj.product_id.id,location_id):
                            lot_id = self.env['stock.production.lot'].search([('id','=',lote[0])])
                            location = self.env['stock.location'].search([('id','=',location_id)])
                            quant = self.env['stock.quant']
                            stock_l = quant._get_available_quantity(so_line_obj.product_id,location,lot_id=lot_id)
                            as_lot_stock +='['+lot_id.name+']-'+str(round(stock_l,2))+','
                            lotes.append(lote[0])
                    if lotes != []:
                        vasl={
                            'product_id': so_line_obj.product_id.id,
                            'route_id': route.id,
                            'location_id': location_id,
                            'lot_ids': lotes,
                            'stock': stock,  
                            'as_lot_stock': as_lot_stock,  
                            'line_id': so_line_obj.id,  
                        }
                        dictlinestock.append([0, 0, vasl])


            #vista de stock de kit lotes-ubicacion
            if so_line_obj.product_id.virtual_available > 0:
                stock = so_line_obj.product_id.qty_available
            for bom in so_line_obj.product_id.bom_ids:
                if  len(bom.bom_line_ids) > 0:
                    menor = so_line_obj.product_id.virtual_available/bom.bom_line_ids[0].product_qty
                for bom_line in bom.bom_line_ids:
                    lotes_row = self.as_get_lotes(bom_line.product_id.id,location_id)
                    lotes = []
                    locations = []
                    for lot in lotes_row:
                        if len(lot) > 0:
                            lotes.append(lot[1])
                            locations.append(lot[0])
                    value = bom_line.product_qty
                    qty = bom_line.product_id.virtual_available/value
                    if  qty < menor:
                        menor=  qty
                    if lotes != []:
                        vasl={
                            'product_id': bom_line.product_id.id,
                            'lot_ids': lotes,
                            'location_ids': locations,
                            'cantidad': bom_line.product_id.qty_available,  
                        }
                        dictline.append([0, 0, vasl])

            res.update({
                'product_id': so_line_obj.product_id.id,
                'udm': so_line_obj.product_id.uom_id.id,
                'udm_sale': so_line_obj.product_uom.id,
                'lines_ids':dictline,
                'lines_stock_ids':dictlinestock,
                'stock':math.floor(menor),
            })
        return res


    def as_get_lotes(self,product_id,location):
        # self.env.cr.execute(
        #     """select sq.location_id,lot_id from stock_production_lot spl 
        #         join stock_quant sq on sq.lot_id = spl.idkkkk
        #         where 
        #         spl.product_id="""+str(product_id)+""" and 
        #         sq.location_id="""+str(location)+""" and 
        #         sq.quantity > 0
        #         group by 1,2"""
        # )
        self.env.cr.execute(
            """select sq.location_id,lot_id from stock_production_lot spl 
                join stock_quant sq on sq.lot_id = spl.id
                where 
                
                sq.quantity > 0
                group by 1,2"""
        )
        lotes=self.env.cr.fetchall()
        return lotes

    def as_get_lotes_location(self,product_id,location_id):
        self.env.cr.execute(
            """select lot_id from stock_production_lot spl 
                join stock_quant sq on sq.lot_id = spl.id
                where 
                sq.location_id="""+str(location_id)+""" and 
                spl.product_id="""+str(product_id)+""" and 
                sq.quantity > 0
                """
        )
        lotes=self.env.cr.fetchall()
        return lotes

    def as_get_lotes_stock(self,product_id,location_id):
        self.env.cr.execute(
            """select sq.product_id,sum(sq.quantity) from stock_quant sq
                where 
                sq.location_id="""+str(location_id)+""" and 
                sq.product_id="""+str(product_id)+""" and 
                sq.quantity > 0
                group by 1"""
        )
        lotes=self.env.cr.fetchall()
        return lotes

class AsStockProductLine(models.Model):
    _name = 'as.stock.product.line'
    _description = 'Aprobe sale Wizard'

    product_id = fields.Many2one('product.product', 'Producto')
    default_code = fields.Char('Código', related="product_id.default_code")
    lot_ids = fields.Many2many('stock.production.lot', string='Lotes')
    location_ids = fields.Many2many('stock.location', string='Ubicaciones')
    cantidad = fields.Float('Cantidad')

class AsStockRouteLine(models.Model):
    _name = 'as.stock.route.line'
    _description = 'Aprobe sale Wizard'

    product_id = fields.Many2one('product.product', 'Producto')
    default_code = fields.Char('Código', related="product_id.default_code")
    route_id = fields.Many2one('stock.location.route', 'Ruta')
    location_id = fields.Many2one('stock.location', string='Ubicación')
    lot_ids = fields.Many2many('stock.production.lot', string='Lotes')
    stock = fields.Float('Stock')
    as_lot_stock = fields.Char('Stock Lotes')
    line_id =fields.Many2one('sale.order.line')

    def update_sale_line_route(self):
        if self.line_id:
            self.line_id.write({'route_id':self.route_id.id})
        