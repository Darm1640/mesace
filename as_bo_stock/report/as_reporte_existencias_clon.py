# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
_logger = logging.getLogger(__name__)

def generate_xlsx_report3(self, workbook, data, lines):
    # esto usamos para los filtros
    dict_almacen = [] # declaramos una lista vacia
    dict_aux = [] #declaramos una lista vacia
    if data['form']['as_almacen']: # si el wizard fue chekado en almacenes
        for line in data['form']['as_almacen']: #
            dict_almacen.append('('+str(line)+')')
            dict_aux.append(line)
    else:
        almacenes_internos = self.env['stock.location'].search([('usage', '=', 'internal')])
        for line in almacenes_internos:
            dict_almacen.append('('+str(line.id)+')')
            dict_aux.append(line.id)
    
    if data['form']['as_consolidado']:
        dict_almacen = []
        dict_almacen.append(str(dict_aux).replace('[','(').replace(']',')'))

    dict_productos = []
    if data['form']['as_productos']:
        for line in data['form']['as_productos']:
            dict_productos.append(line)
    if dict_productos:
        filtro_productos = "AND sm.product_id in "+str(dict_productos).replace('[','(').replace(']',')')
    else:
        filtro_productos = ''
        
    #Definiciones generales del archivo, formatos, titulos, hojas de trabajo
    sheet = workbook.add_worksheet('Reporte Existencias')
    titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold':True })
    titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
    titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
    titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
    titulo4 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })

    number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00'})
    number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
    number_right_bold = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
    number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
    number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
    number_right_col.set_locked(False)

    letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
    letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
    letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
    letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
    letter_locked = letter3
    letter_locked.set_locked(False)

    # Aqui definimos en los anchos de columna
    sheet.set_column('A:A',15, letter1)
    sheet.set_column('B:B',30, letter1)
    sheet.set_column('C:C',15, letter1)
    sheet.set_column('D:D',18, letter1)
    sheet.set_column('E:E',15, letter1)
    sheet.set_column('F:F',15, letter1)
    sheet.set_column('G:G',15, letter1)
    sheet.set_column('H:H',15, letter1)
    sheet.set_column('I:I',15, letter1)
    sheet.set_column('J:J',15, letter1)
    sheet.set_column('K:K',15, letter1)

    # Titulos, subtitulos, filtros y campos del reporte
    sheet.merge_range('A1:H1', 'REPORTE DE EXISTENCIAS DE PRODUCTOS', titulo1)

    fecha_inicial = datetime.strptime(data['form']['start_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
    fecha_final = datetime.strptime(data['form']['end_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
    sheet.write(1, 0, 'Rango de Fechas: ', letter4)
    sheet.merge_range('B2:D2', fecha_inicial +' - '+ fecha_final)
    sheet.write(2, 0, 'Almacen: ', letter4)
    filtro_almacenes_name = 'VARIOS'
    for y in dict_aux:
        almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
        filtro_almacenes_name += ', '+almacen_obj.name
    if len(dict_aux)==1 and not data['form']['as_consolidado']:
        filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
    sheet.merge_range('B3:D3', filtro_almacenes_name)

    sheet.merge_range('A4:A5', 'Codigo Producto', titulo4)
    sheet.merge_range('B4:D5', 'Categiria/Linea/Marca/Producto', titulo4)
    sheet.merge_range('E4:E5', 'UdM', titulo4)
    sheet.merge_range('F4:F5', 'Precio de Costo', titulo4)
    sheet.merge_range('G4:G5', 'Cantidad', titulo4)
    sheet.merge_range('H4:H5', 'Valorado Bs.', titulo4)
    sheet.freeze_panes(5, 0)
    valor = self.env.user.company_id.currency_id.rounding
    filas = 4
    row_totals = {}
    row_totals['rows'] = {}
    row_totals['cantidad'] = {}
    row_totals['valorado'] = {}

    for almacen in dict_almacen:
        filas += 1
        row_totals['rows'][almacen] = filas
        if almacen not in row_totals['cantidad']: row_totals['cantidad'][almacen] = 0
        if almacen not in row_totals['valorado']: row_totals['valorado'][almacen] = 0
        if data['form']['as_consolidado']:
            sheet.merge_range('A'+str(filas+1)+':D'+str(filas+1), 'CONSOLIDADO', titulo2)
        else:
            id_almacen = int(str(almacen).replace('(','').replace(')',''))
            almacen_obj = self.env['stock.location'].search([('id', '=', id_almacen)], limit=1)
            sheet.merge_range('A'+str(filas+1)+':D'+str(filas+1), almacen_obj.name, titulo2)
        join_categ = ' LEFT JOIN product_category pc1 ON pc1.id = pt.categ_id '
        result_categ = ",COALESCE(pc1.name, 'No asignado') "
        order_by = ' ORDER BY 3'
        level_names = {}

        for i in range(data['form']['as_categ_levels']):
            pc_number = i+1
            order_number = i+3
            level_names[i+2] = ''
            if pc_number > 1:
                join_categ += ' LEFT JOIN product_category pc'+str(pc_number)+' ON pc'+str(pc_number)+'.id = pc'+str(pc_number-1)+'.parent_id '
                tmp_str = " ,COALESCE(pc"+str(pc_number)+".name, 'No asignado') "
                result_categ = tmp_str + result_categ
            if order_number > 3:
                order_by += ' , '+str(order_number)

        order_by += ' , 2'         

        query_ids = ("""
            SELECT
                pp.id as "ID"
                ,CONCAT(pp.default_code, ' - ', pt.name) as "Codigo Producto"
                """+result_categ+"""
                ,pu.name
            FROM
                product_product pp
                INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                INNER JOIN uom_uom pu ON pu.id = pt.uom_id
                """+join_categ+"""
            WHERE
                pp.id in
                (SELECT
                    sm.product_id
                FROM
                    stock_move sm
                    LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
	 	            LEFT JOIN stock_inventory si ON si.id = sm.inventory_id
                WHERE
                    sm.state = 'done'
                    AND (sm.location_id IN """+str(almacen)+"""
                    OR sm.location_dest_id IN """+str(almacen)+""")
                    
                    AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(data['form']['end_date'])+"""'
                    """+filtro_productos+"""
                GROUP BY 1)
            """+order_by+"""
        """)
        
        _logger.debug("\n\n Query 1 EXISTENCIAS %s\n\n",query_ids)
        self.env.cr.execute(query_ids)

        product_categories = [j for j in self.env.cr.fetchall()]

        for producto in product_categories:
            query_movements = ("""
                SELECT
                    pp.default_code as "Codigo Producto"
                    ,CONCAT(COALESCE(sp.name, sm.name), ' - ', COALESCE(sp.origin, 'S/Origen')) as "Comprobante"
                    ,COALESCE((sp.date_done AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date, sm.date::date) as "Fecha"
                    ,COALESCE(rp.name,'SIN NOMBRE') as "Cliente/Proveedor"
                    ,CASE 
                        WHEN (sm.location_dest_id IN """+str(almacen)+""" AND sm.location_id NOT IN """+str(almacen)+""") THEN sm.product_qty
                        WHEN (sm.location_id IN """+str(almacen)+""" AND sm.location_dest_id NOT IN """+str(almacen)+""") THEN -sm.product_qty
                        ELSE 0 END as "Cantidad"
                    ,COALESCE(sm.price_unit, 0) as "Costo"
                     
                    
                    FROM
                        stock_move sm
                        LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                        LEFT JOIN product_product pp ON pp.id = sm.product_id
                        LEFT JOIN res_partner rp ON rp.id = sp.partner_id
                    WHERE
                        sm.state = 'done'
                        AND (sm.location_id IN """+str(almacen)+""" or sm.location_dest_id IN """+str(almacen)+""")
                        AND pp.id = """+str(producto[0])+"""
                        AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(data['form']['end_date'])+"""'
                    ORDER BY COALESCE(sp.date_done, sm.date)  asc
            """)
            _logger.debug("\n\n Query 2 EXISTENCIAS %s\n\n",query_movements)
            #linea 179 ,sp.as_ufv  ,sm.as_ufv_sm
            self.env.cr.execute(query_movements)
            # all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
            movimientos_almacen = []
            
            for k in self.env.cr.fetchall():
                movimientos_almacen.append(k)
                saldo_UFV = 0.0
                
                # if k[6]==True:
                    #res = self.get_saldo_entrada(producto[0],almacen,str(data['form']['end_date']))
                if k[7]!= None:
                    saldo_UFV = (k[7])
                    

                row_totals['cantidad'][almacen] += k[4]
                row_totals['valorado'][almacen] += (k[4]*k[5])+saldo_UFV
                posicion = almacen+','
                for x in range(data['form']['as_categ_levels']):
                    level = x+2
                    posicion += producto[level]+','
                    if posicion not in row_totals['cantidad']: row_totals['cantidad'][posicion] = 0
                    if posicion not in row_totals['valorado']: row_totals['valorado'][posicion] = 0
                    row_totals['cantidad'][posicion] += k[4]
                    row_totals['valorado'][posicion] += (k[4]*k[5])+saldo_UFV
                posicion += str(producto[0])
                if posicion not in row_totals['cantidad']: row_totals['cantidad'][posicion] = 0
                if posicion not in row_totals['valorado']: row_totals['valorado'][posicion] = 0
                row_totals['cantidad'][posicion] += k[4]
                row_totals['valorado'][posicion] += (k[4]*k[5])+saldo_UFV

            #si encontramos movimientos pasamos a la impresion
            if movimientos_almacen or saldo_inicial:
                blanco = ''
                posicion = almacen+','
                for x in range(data['form']['as_categ_levels']):
                    level = x+2
                    if level>2: blanco += '      '
                    posicion += producto[level]+','
                    if producto[level] != level_names[level]:
                        filas += 1
                        row_totals['rows'][posicion] = filas
                        sheet.set_row(filas, None, None, {'level': level-1})
                        sheet.merge_range('A'+str(filas+1)+':D'+str(filas+1), blanco + producto[level], letter2)
                        level_names[level] = producto[level]
                posicion += str(producto[0])

                ides = self.env['product.product'].search([('id', '=', producto[0])])


                if data['form']['as_include_qty']:
                    filas += 1
                    row_totals['rows'][posicion] = filas
                    sheet.write(filas, 0, producto[1].split(' - ')[0]) 
                    sheet.merge_range('B'+str(filas+1)+':D'+str(filas+1), ides.display_name)
                    sheet.write(filas, 4, producto[-1])
                    sheet.set_row(filas, None, None, {'level': data['form']['as_include_qty']+1})
                
                elif not data['form']['as_include_qty'] and row_totals['cantidad'][posicion] != 0:
                    filas += 1
                    row_totals['rows'][posicion] = filas
                    sheet.write(filas, 0, producto[1].split(' - ')[0])
                    sheet.merge_range('B'+str(filas+1)+':D'+str(filas+1), ides.display_name)
                    sheet.write(filas, 4, producto[-1])
                    sheet.set_row(filas, None, None, {'level': data['form']['as_include_qty']+1})
    
    for row in row_totals['rows']:
        total_cantidad = row_totals['cantidad'][row] if row in row_totals['cantidad'] else 0.0
        total_valorado = row_totals['valorado'][row] if row in row_totals['valorado'] else 0.0
        precio_costo   = (total_valorado/total_cantidad) if total_cantidad != 0 else 0.0
        sheet.write(row_totals['rows'][row], 5, precio_costo, number_right_bold)
        sheet.write(row_totals['rows'][row], 6, total_cantidad, number_right_bold)
        sheet.write(row_totals['rows'][row], 7, total_valorado, number_right_bold)
                

    def get_saldo_entrada(self,product,almacen,fecha):
        year = (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
        ultimo_dia_year = year+'-'+'12'+'-'+'31'
        #tomamos 
        query_movements = ("""
            SELECT
                pp.default_code as "Codigo Producto"
                ,CONCAT(COALESCE(sp.name, sm.name), ' - ', COALESCE(sp.origin, 'S/Origen')) as "Comprobante"
                ,COALESCE(sp.date_done::date, sm.date::date) as "Fecha"
                ,COALESCE(rp.name,'SIN NOMBRE') as "Cliente/Proveedor"
                ,CASE 
                    WHEN (sm.location_dest_id IN """+str(almacen)+""" AND sm.location_id NOT IN """+str(almacen)+""") THEN sm.product_qty
                    WHEN (sm.location_id IN """+str(almacen)+""" AND sm.location_dest_id NOT IN """+str(almacen)+""") THEN -sm.product_qty
                    ELSE 0 END as "Cantidad"
                ,COALESCE(sm.price_unit, 0) as "Costo"
            FROM
                stock_move sm
                LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON pp.id = sm.product_id
                LEFT JOIN res_partner rp ON rp.id = sp.partner_id
            WHERE
                
                sm.state = 'done'
                AND (sm.location_id IN """+str(almacen)+""" or sm.location_dest_id IN """+str(almacen)+""")
                AND pp.id = """+str(product)+"""
                AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(fecha)+"""'
            ORDER BY COALESCE(sp.date_done::date, sm.date::date)  asc
        """)
        self.env.cr.execute(query_movements)
        #linea 290 sp.as_ufv = 'True' AND
        _logger.debug("\n\saldo entrada: EXISTENCIAS %s\n\n",query_movements)
        ultimo_monto = [k for k in self.env.cr.fetchall()]
        total= 0.0
        stock= 0.0
        bandera = False
        fecha_ininial = ''
        fecha_ultimo = ''
        for stock_move in ultimo_monto:
            fecha_ultimo = stock_move[2]
            total_ingreso = 0.0
            total_egreso= 0.0
            stock_ingreso = 0.0
            stock_egreso= 0.0
            if stock_move[4]>0:
                fecha_ininial = stock_move[2]
                total_ingreso = stock_move[5]*abs(stock_move[4])
                stock_ingreso = abs(stock_move[4])
            if stock_move[4]<0:
                total_egreso = stock_move[5]*abs(stock_move[4])
                stock_egreso = abs(stock_move[4])
            if bandera:
                total= total_ingreso - total_egreso + total
                stock= stock_ingreso - stock_egreso + stock
            else:
                total = total_ingreso - total_egreso
                stock= stock_ingreso - stock_egreso 
                bandera = True
        if fecha_ininial=='':
            fecha_ininial = ultimo_dia_year
        ufv_inicial = float(self.get_rate_ufv_start(fecha_ininial))
        ufv_final = float(self.get_rate_ufv_end(ultimo_dia_year))
        monto_actualizacon = total*(ufv_final/ufv_inicial)
        if stock > 0:
            precio_costo = monto_actualizacon / stock
        else:
            precio_costo = 0
        diferencia =monto_actualizacon-total
        vals = {
            'fecha': (datetime.strptime(str(ultimo_dia_year), '%Y-%m-%d')).strftime('%d/%m/%Y'),
            'PU': precio_costo,
            'stock': stock,
            'total': monto_actualizacon,
            'diff': diferencia,
        }
        return vals
    
    def get_rate_ufv_end(self,fecha):
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '<=', fecha),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        return as_ufv_actual

    def get_rate_ufv_start(self,fecha):
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', fecha),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        return as_ufv_ant
