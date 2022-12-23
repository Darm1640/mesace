# -*- coding: utf-8 -*-

from odoo import api, models,fields,_
from odoo.tools import pycompat,float_is_zero
from odoo.tools.float_utils import float_round

class product_product(models.Model):
    _inherit = 'product.product'

    price_unit = fields.Float(
        string='Costo',
        help='Outgoing for product specified on the context',
    )

    def _prepare_out_svl_vals(self, quantity, company):
        """Prepare the values for a stock valuation layer created by a delivery.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        self.ensure_one()
        # Quantity is negative for out valuation layers.
        quantity =  quantity
        vals = {
            'product_id': self.id,
            'value': quantity * self.standard_price,
            'unit_cost': self.standard_price,
            'quantity': quantity,
        }
        if self.cost_method in ('average', 'fifo'):
            fifo_vals = self._run_fifo(abs(quantity), company)
            vals['remaining_qty'] = fifo_vals.get('remaining_qty')
            if self.cost_method == 'fifo':
                vals.update(fifo_vals)
        return vals

    def _get_domain_locations(self):
        """
        Overwrite core method to add check of user's default warehouse.

        The goal is to show available quantities only for default user warehouse
        While locations table show all stocks
        """
        def_warehouse = self.env.user.default_warehouse
        if not (self._context.get('warehouse', False) or self._context.get('location', False)) \
                and def_warehouse:
            res = super(product_product, self.with_context(warehouse=def_warehouse.id))._get_domain_locations()
        else:
            res = super(product_product, self)._get_domain_locations()
        return res

    def action_prepare_xlsx_balance_product(self):
        """
        To trigger the method of template
        """
        res = self.product_tmpl_id.action_prepare_xlsx_balance()
        return res

    def action_updates_cost(self):
        product_product = self
        self.env.cr.execute("""
            SELECT
                sl.id
            FROM
                stock_location sl
                INNER JOIN stock_move sm ON (sm.location_id = sl.id OR sm.location_dest_id = sl.id)
                INNER JOIN product_product pp ON pp.id = sm.product_id
            WHERE
                sl.usage = 'internal'
                AND pp.id = """+str(self.id)+"""
            GROUP BY 1
        """)
        ubicaciones_ids = [i[0] for i in self.env.cr.fetchall()]
        for ubicacion in ubicaciones_ids:
            precio = self.actualizar_costos_producto_movimiento(product_product.id, ubicacion)
            stock_quant = self.env['stock.quant'].sudo().search([('product_id', '=', product_product.id),('location_id', '=', ubicacion)], order='id desc',limit=1)
            stock_quant.update({'value_unit':precio,'value':stock_quant.quantity*precio})
            self.standard_price =precio
        _logger.debug("_costo_actualizado: %s - %s",self.id,self.name)
        

    # Funcion individual de actualizar el costo y stock por almacen
    def actualizar_costos_producto_movimiento(self, producto_id, location_id):
        ultimo_costo = 0
        ajuste = False
        moduleObj_MRP = self.env['ir.module.module'].sudo().search([("name","=","mrp"),("state","=","installed")])
        consulta = ("""
            SELECT
            sm.purchase_line_id
            ,sm.product_id
            ,COALESCE(sm.price_unit,0)
            ,COALESCE(sm.product_qty,0)
            ,sm.picking_type_id
            ,sm.location_id AS origen
            ,sm.location_dest_id AS destino
            ,sm.inventory_id
            ,sm.id
            ,sm.date
            ,'-'
            ,sm.origin
            ,destino.usage
            ,sm.origin_returned_move_id
            ,spt.default_location_dest_id
            ,spt.code
            FROM stock_move AS sm
            LEFT JOIN stock_location ubicacion ON ubicacion.id=sm.location_id 
            LEFT JOIN stock_location destino ON destino.id=sm.location_dest_id
            LEFT JOIN stock_move sm2 ON sm2.id=sm.origin_returned_move_id
            LEFT JOIN stock_picking_type spt ON spt.id=sm2.picking_type_id
            JOIN stock_picking sp ON sp.id=sm.picking_id
            WHERE sm.state IN ('done')  
            AND (ubicacion.id="""+str(location_id)+""" OR destino.id="""+str(location_id)+""")
            AND sm.product_id="""+str(producto_id)+"""
            ORDER BY COALESCE(sp.date_done, sm.date)  asc
        """)
        self.env.cr.execute(consulta)
        res_consulta = [j for j in self.env.cr.fetchall()]

        cantidad = total_costo = price_unit = 0
        bandera = False
        for move in res_consulta:
            if (location_id == move[6] and location_id != move[5]): #ingresos
                if cantidad == 0:
                    bandera = True
                if move[13]:
                    if move[15] == 'outgoing': # Devoluciones
                        price_unit = ultimo_costo
                    cantidad += move[3]
                    total_costo += price_unit * move[3]
                elif moduleObj_MRP: # Ordenes de produccion
                    mrp_produccion = self.env['mrp.production'].sudo().search([('name', '=', move[11]), ('product_id', '=', move[1])], limit=1)
                    if mrp_produccion:
                        total_valorado = 0
                        for line in mrp_produccion.move_raw_ids:
                            total_valorado += line.price_unit*line.product_qty
                        price_unit = total_valorado/move[3] if move[3]!=0 else 0.0
                        cantidad += move[3]
                        total_costo += move[3]*price_unit
                                       
                    else:
                        price_unit = move[2]
                        if price_unit == 0:
                            price_unit = ultimo_costo
                        cantidad += move[3]
                        total_costo += price_unit * move[3]
                else: #otros ingresos
                    price_unit = move[2]
                    if price_unit == 0:
                        price_unit = ultimo_costo
                    cantidad += move[3]
                    total_costo += price_unit * move[3]
                if cantidad != 0 and bandera == False:
                    ultimo_costo = total_costo/cantidad
                elif bandera:
                    ultimo_costo = price_unit
                    bandera = False

            elif location_id == move[5] and location_id != move[6]: #salidas
                price_unit = total_costo/cantidad if cantidad!=0 else 0
                cantidad -= move[3]
                if price_unit == 0 or cantidad <= 0:
                    price_unit = ultimo_costo
                # if move[12] == 'internal': # Salidas en transferencias entre almacenes
                #     #price_unit = move[2] or 0
                #     price_unit = ultimo_costo
                total_costo -= price_unit * move[3]
            
            elif location_id == move[5] and location_id == move[6]: #transferencia interna ? (no deberia darse el caso)
                price_unit = ultimo_costo
                
            # vamos a guardar el ultimo costo para las transferencias en caso de quedar el saldo en 0
            # if price_unit != 0:
            #     ultimo_costo = price_unit
            
            self.env.cr.execute("UPDATE stock_move SET price_unit="+str(abs(price_unit))+" WHERE id="+str(move[8]))
        return price_unit

