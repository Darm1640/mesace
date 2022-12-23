# -*- coding: utf-8 -*-

import base64
import logging
import tempfile

from odoo import _, api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("Cannot import xlsxwriter")
    xlsxwriter = False


class product_template(models.Model):
    _inherit = 'product.template'

    price_unit = fields.Float(
        string='Costo',
        help='Outgoing for product specified on the context',
    )

    def _compute_location_ids(self):
        """
        Compute method for location_ids - as all internal locations

        Extra info:
         * To show only viable location (with positive inventories) we filter locations already in js
         * We should include inactive locations, since configurable inputs are deactivated
         * No restrictionon company_id, since it managed by security rules
        """
        for product_id in self:
            location_ids = self.env["stock.location"].search([
                ('usage', '=', 'internal'),
                "|",
                    ("active", "=", True),
                    ("active", "=", False),
            ])
            product_id.location_ids = [(6, 0, location_ids.ids)]

    def _inverse_location_ids(self):
        """
        Inverse method for location_ids: dummy method so that we can edit vouchers and save changes
        """
        return True

    location_ids = fields.One2many(
        'stock.location',
        compute=_compute_location_ids,
        inverse=_inverse_location_ids,
        string='Locations',
    )

    def action_prepare_xlsx_balance(self):
        """
        The method to make .xlsx table of stock balances

        1. Prepare workbook and styles
        2. Prepare header row
          2.1 Get column name like 'A' or 'S' (ascii char depends on counter)
        3. Prepare each row of locations
        4. Create an attachment

        Returns:
         * action of downloading the xlsx table

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_("The Python library xlsxwriter is installed. Contact your system administrator"))
        # 1
        file_path = tempfile.mktemp(suffix='.xlsx')
        workbook = xlsxwriter.Workbook(file_path)
        styles = {
            'main_header_style': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'border': 1,
            }),
            'main_data_style': workbook.add_format({
                'font_size': 11,
                'border': 1,
            }),
        }
        worksheet = workbook.add_worksheet(u"{}#{}.xlsx".format(self.name, fields.Date.today()))
        # 2
        cur_column = 0
        for column in [_("Location"), _("On Hand"), _("Forecast"), _("Incom"), _("Out")]:
            worksheet.write(0, cur_column, column, styles.get("main_header_style"))
            # 2.1
            col_letter = chr(cur_column + 97).upper()
            column_width = cur_column == 0 and 60 or 8
            worksheet.set_column('{c}:{c}'.format(c=col_letter), column_width)
            cur_column += 1
        # 3
        elements = []
        for loc in self.location_ids:
            balances = loc._return_balances()
            if balances:
                elements.append({
                    "name": loc.name,
                    "id": loc.id,
                    "qty_available": balances.get("qty_available"),
                    "incoming_qty": balances.get("incoming_qty"),
                    "outgoing_qty": balances.get("outgoing_qty"),
                    "virtual_available": balances.get("virtual_available"),
                })
        elements = self.env["stock.location"].prepare_elements_for_hierarchy(args={"elements": elements})
        row = 1
        for loc in elements:
            spaces = ""
            level = loc.get("level")
            itera = 0
            while itera != level:
                spaces += "    "
                itera += 1
            instance = (
                spaces + loc.get("name"),
                loc.get("qty_available"),
                loc.get("virtual_available"),
                loc.get("incoming_qty"),
                loc.get("outgoing_qty"),
            )
            for counter, column in enumerate(instance):
                value = column
                worksheet.write(
                    row,
                    counter,
                    value,
                    styles.get("main_data_style")
                )
            row += 1
        workbook.close()
        # 4
        with open(file_path, 'rb') as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            'name':  u"{}#{}.xlsx".format(self.name, fields.Date.today()),
            'type': 'binary',
            'datas': xls_file,
            'datas_fname': u"{}#{}.xlsx".format(self.name, fields.Date.today()),
        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        self.env.cr.commit()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id,),
            'target': 'self',
        }
        return action

    def action_updates_cost(self):
        product_product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', self.id)], limit=1)
        self.env.cr.execute("""
            SELECT
                sl.id
            FROM
                stock_location sl
                INNER JOIN stock_move sm ON (sm.location_id = sl.id OR sm.location_dest_id = sl.id)
                INNER JOIN product_product pp ON pp.id = sm.product_id
            WHERE
                sl.usage in ('internal','inventory')
                AND pp.product_tmpl_id = """+str(self.id)+"""
            GROUP BY 1
        """)
        ubicaciones_ids = [i[0] for i in self.env.cr.fetchall()]
        for ubicacion in ubicaciones_ids:
            precio = self.actualizar_costos_producto_movimiento(product_product.id, ubicacion)
            stock_quant = self.env['as.valuation.location'].sudo().search([('product_id', '=', product_product.id),('location_id', '=', ubicacion)],order='id desc', limit=1)
            stock_quant.update({'unit_cost':precio})
            self.standard_price = precio
        

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
            LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
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
            if move[0]:
                move_line = self.env['stock.move'].search([('id','=',move[8])])
                move_line.price_unit = move_line._get_price_unit()
                # move_line.price_unit = move_line.purchase_line_id.currency_id._convert(move_line.purchase_line_id.price_unit, move_line.purchase_line_id.company_id.currency_id, move_line.purchase_line_id.company_id, move_line.date,round=False)              
                if move_line.purchase_line_id.order_id.as_importacion and move_line.as_price_unit_import > 0:
                    move_line.price_unit = move_line.purchase_line_id.currency_id._convert(move_line.as_price_unit_import, move_line.purchase_line_id.company_id.currency_id, move_line.purchase_line_id.company_id, move_line.date,round=False) 
                   
            # if 16 in move:
            #     ajsute = move[16]
            # else:
            #     ajsute = False
            price_unit = float(move[2])
            if (location_id == move[6] and location_id != move[5]) : #ingresos
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
                    
                    # elif ajsute ==True:
                    #     price_unit = move[2]
                    #     if price_unit == 0:
                    #         price_unit = ultimo_costo
                    #     cantidad = move[3]
                    #     total_costo = price_unit * move[3]                    
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
            

class product_product(models.Model):
    _inherit = 'product.product'


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
                sl.usage in ('internal','inventory')
                AND pp.id = """+str(self.id)+"""
            GROUP BY 1
        """)
        ubicaciones_ids = [i[0] for i in self.env.cr.fetchall()]
        for ubicacion in ubicaciones_ids:
            precio = self.actualizar_costos_producto_movimiento(product_product.id, ubicacion)
            stock_quant = self.env['as.valuation.location'].sudo().search([('product_id', '=', product_product.id),('location_id', '=', ubicacion)],order='id desc', limit=1)
            for x in stock_quant:
                stock_quant.update({'unit_cost':precio})
            self.standard_price =precio
        

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
            LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
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
            if move[0]:
                move_line = self.env['stock.move'].search([('id','=',move[8])])
                move_line.price_unit = move_line._get_price_unit()
                if move_line.purchase_line_id.order_id.as_importacion and move_line.as_price_unit_import > 0:
                    move_line.price_unit = move_line.purchase_line_id.currency_id._convert(move_line.as_price_unit_import, move_line.purchase_line_id.company_id.currency_id, move_line.purchase_line_id.company_id, move_line.date,round=False) 
                
                # move_line.purchase_line_id.currency_id._convert(move_line.purchase_line_id.price_unit, move_line.purchase_line_id.company_id.currency_id, move_line.purchase_line_id.company_id, move_line.date,round=False)
            # if 16 in move:
            #     ajsute = move[16]
            # else:
            #     ajsute = False
            price_unit = float(move[2])
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
                    
                    # elif ajsute ==True:
                    #     price_unit = move[2]
                    #     if price_unit == 0:
                    #         price_unit = ultimo_costo
                    #     cantidad = move[3]
                    #     total_costo = price_unit * move[3]                    
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
              
                total_costo -= price_unit * move[3]
            
            elif location_id == move[5] and location_id == move[6]: #transferencia interna ? (no deberia darse el caso)
                price_unit = ultimo_costo
            
            self.env.cr.execute("UPDATE stock_move SET price_unit="+str(abs(price_unit))+" WHERE id="+str(move[8]))
        return price_unit

    def actualizar_stock_productos(self, location_id):
        self.ensure_one()
        stock_total = 0.0
        context = self._context
        ahora = fields.Date.today()
        d1 = ahora.strftime("%Y-%m-%d")
        if self.tracking == 'lot': 
            lot_ids = self.env['stock.production.lot'].search([('product_id', '=', self.id)], order="name asc")
            for lot in lot_ids:
                sql = ("""
                    SELECT
                    spl.id,
                    SUM(CASE
                        WHEN (sm.location_dest_id IN ("""+str(location_id)+""") AND sm.location_id NOT IN ("""+str(location_id)+""")) THEN sm.qty_done
                        WHEN (sm.location_id IN ( """+str(location_id)+""") AND sm.location_dest_id NOT IN ("""+str(location_id)+""")) THEN -sm.qty_done
                        ELSE 0 END) as "Cantidad"

                    FROM
                        stock_move_line sm     
                        LEFT JOIN product_product pp ON pp.id = sm.product_id
                        LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                        LEFT JOIN res_partner rp ON rp.id = sp.partner_id
                        left join stock_production_lot spl on spl.id = sm.lot_id
                    WHERE
                        sm.state = 'done' 
                        AND (sm.location_id IN ("""+str(location_id)+""") or sm.location_dest_id IN ("""+str(location_id)+"""))
                        AND pp.id = '"""+str(self.id)+"""'  
                        AND spl.id = '"""+str(lot.id)+"""'  
                        AND COALESCE((sp.date_done AT TIME ZONE 
                        'UTC' AT TIME ZONE 'BOT')::date, sm.date::date) <= ' """ + d1 +""" '  
                    
                    GROUP BY 1
                        """)
                _logger.debug(sql)
                self.env.cr.execute(sql)
                all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
                stock_quant = self.env['stock.quant'].sudo().search([('product_id', '=', self.id),('location_id', '=', location_id),('lot_id', '=', lot.id)],order='id desc', limit=1)
                if all_movimientos_almacen:
                    for move_line in all_movimientos_almacen:
                        if stock_quant:
                            stock_quant.quantity = move_line[1]
                        elif move_line[1]>0:
                            vals = {
                                'product_id': self.id,
                                'product_uom_id': self.uom_id.id,
                                'location_id': location_id,
                                'quantity': move_line[1],
                                'lot_id': move_line[0],
                                'reserved_quantity': 0,
                            }
                            self.env['stock.quant'].create(vals)
                        stock_total += move_line[1]
                elif not all_movimientos_almacen and stock_quant:
                    stock_quant.quantity = 0.0
        else:
            sql = ("""
                SELECT
                pp.id,
                SUM(CASE
                    WHEN (sm.location_dest_id IN ("""+str(location_id)+""") AND sm.location_id NOT IN ("""+str(location_id)+""")) THEN sm.qty_done
                    WHEN (sm.location_id IN ( """+str(location_id)+""") AND sm.location_dest_id NOT IN ("""+str(location_id)+""")) THEN -sm.qty_done
                    ELSE 0 END) as "Cantidad"

                FROM
                    stock_move_line sm     
                    LEFT JOIN product_product pp ON pp.id = sm.product_id
                    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                    LEFT JOIN res_partner rp ON rp.id = sp.partner_id
                WHERE
                    sm.state = 'done' 
                    AND (sm.location_id IN ("""+str(location_id)+""") or sm.location_dest_id IN ("""+str(location_id)+"""))
                    AND pp.id = '"""+str(self.id)+"""'  
                    AND COALESCE((sp.date_done AT TIME ZONE 
                    'UTC' AT TIME ZONE 'BOT')::date, sm.date::date) <= ' """ + d1 +""" '  
                
                GROUP BY 1
                    """)
            _logger.debug(sql)
            self.env.cr.execute(sql)
            all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
            stock_quant = self.env['stock.quant'].sudo().search([('product_id', '=', self.id),('location_id', '=', location_id)],order='id desc', limit=1)
            if all_movimientos_almacen:
                for move_line in all_movimientos_almacen:
                    if stock_quant:
                        stock_quant.quantity = move_line[1]
                    elif move_line[1]>0:
                        vals = {
                            'product_id': self.id,
                            'product_uom_id': self.uom_id.id,
                            'location_id': location_id,
                            'quantity': move_line[1],
                            'reserved_quantity': 0,
                        }
                        self.env['stock.quant'].create(vals)
                    stock_total += move_line[1]
            elif not all_movimientos_almacen and stock_quant:
                stock_quant.quantity = 0.0

                
        return stock_total
