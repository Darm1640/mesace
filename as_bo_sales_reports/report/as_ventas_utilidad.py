
import xlwt
import datetime
import xlsxwriter
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
from dateutil import relativedelta
import time
import locale
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.tools.translate import _
import base64
from io import BytesIO
from odoo.tools.image import image_data_uri
import locale
from odoo import netsvc
from odoo import tools
from urllib.request import urlopen
from time import mktime
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class as_ventas_utilidad(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.informe_utilidad.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        dict_almacen = []
        dict_aux = []
        filtro_almacen = ''
        if data['form']['as_almacen']:
            for line in data['form']['as_almacen']:
                dict_almacen.append('(' + str(line) + ')')
                dict_aux.append(line)
            filtro_almacen = "AND sp.location_id IN "+str(dict_aux).replace('[','(').replace(']',')')
            "AND sl.id in "+str(dict_almacen).replace('[','(').replace(']',')')
        else:
            almacenes_internos = self.env['stock.location'].search([('usage', '=', 'internal')])
            for line in almacenes_internos:
                dict_almacen.append('(' + str(line.id) + ')')
                dict_aux.append(line.id)

        # Obtenemos en una variable si el reporte es Pos, Ventas o ambos
        fuente, fuente_str = data['form']['as_fuente'], ''
        if fuente == 'both':
            fuente_str = 'POS y VENTAS'
        else:
            fuente_str = 'POS' if fuente == 'po' else 'VENTAS'

        if data['form']['as_consolidado']:
            dict_almacen = []
            dict_almacen.append(str(dict_aux).replace('[', '(').replace(']', ')'))

        dict_productos = []
        if data['form']['as_productos']:
            for line in data['form']['as_productos']:
                dict_productos.append(line)
        if dict_productos:
            filtro_productos = "AND sm.product_id in " + str(dict_productos).replace('[', '(').replace(']', ')')
        else:
            filtro_productos = ''

        # Definiciones generales del archivo, formatos, titulos, hojas de trabajo
        sheet = workbook.add_worksheet('Detalle de Movimientos')
        titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
        titulo3 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3_number = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00'})
        number_right_bold = workbook.add_format(
            {'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'bold': True})
        number_right_col = workbook.add_format(
            {'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 10, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': True})
        letter3 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A', 30, letter1)
        sheet.set_column('B:B', 15, letter1)
        sheet.set_column('C:C', 15, letter1)
        sheet.set_column('D:D', 15, letter1)
        sheet.set_column('E:E', 15, letter1)
        sheet.set_column('F:F', 15, letter1)
        sheet.set_column('G:G', 15, letter1)
        sheet.set_column('H:H', 15, letter1)
        sheet.set_column('I:I', 15, letter1)
        sheet.set_column('J:J', 20, letter1)
        sheet.set_column('K:K', 20, letter1)
        #todo terminas hasta letra K
        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A4:K4', 'INFORME DE VENTAS Y UTILIDAD', titulo1)
        
        fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        sheet.merge_range('A5:K5', fecha_inicial + ' - ' + fecha_final,titulo2)
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A2', url, {'image_data': image_data,'x_scale': 0.32, 'y_scale': 0.12})
        filastitle=9
        sheet.write(7, 0, 'Almacen: ', titulo4)
        filtro_almacenes_name = 'VARIOS'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name
        if len(dict_aux) == 1 and not data['form']['as_consolidado']:
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        sheet.merge_range('B8:C8', filtro_almacenes_name,titulo3)
        sheet.write(8, 0, 'Usuario:', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(0, 9, 'NIT: ', titulo3) 
        sheet.write(1, 9, 'DIRECCION: ', titulo3) 
        sheet.write(2, 9, 'CELULAR, TELEFONO:', titulo3)   
        sheet.write(7, 9, 'Fecha de impresion: ', titulo4)
        sheet.write(7, 10, fecha_actual, titulo3)
        sheet.write(8, 9, 'Fuente : ', titulo4)
        sheet.write(8,10, fuente_str,titulo3)

        sheet.write(10, 0, 'DETALLE', tituloAzul)
        sheet.write(10, 1, 'UNIDAD DE MEDIDA', tituloAzul)
        sheet.write(10, 2, 'CANTIDAD', tituloAzul)
        sheet.write(10, 3, 'PRECIO DE COSTO', tituloAzul)
        sheet.write(10, 4, 'PRECIO UNITARIO VENTA', tituloAzul)
        sheet.write(10, 5, 'VENTA BRUTA', tituloAzul)
        sheet.write(10, 6, 'IVA DEBITO', tituloAzul)
        sheet.write(10, 7, 'VENTA NETA', tituloAzul)
        sheet.write(10, 8, 'COSTO TOTAL DE COMPRA', tituloAzul)
        sheet.write(10, 9, 'MARGEN DE GANANCIA', tituloAzul)
        sheet.write(10, 10, '%', tituloAzul)
        sheet.freeze_panes(5, 0)

        filas = 11

        vendedores_dict = {}  # {v_id: {almacen_id: [detalle_utilidad_1,...,detalle_utilidad_n]}}
        level_name_dict = {}
        product_categories_dict = {}
        filtro_fechas_po = " AND (sm.date::TIMESTAMP+ '-4 hr')::date >= '""" + str(data['form']['start_date']) + "' AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '" + str(data['form']['end_date']) + "'"

        # aca se agrupa por almacenes
        for almacen in dict_aux:
            join_categ = ' LEFT JOIN product_category pc1 ON pc1.id = pt.categ_id '
            result_categ = ",COALESCE(pc1.name, 'No asignado') "
            order_by = ' ORDER BY 3'
            level_names = {}

            for i in range(data['form']['as_categ_levels']):
                pc_number = i + 1
                order_number = i + 3
                level_names[i + 2] = ''
                if pc_number > 1:
                    join_categ += ' LEFT JOIN product_category pc' + str(pc_number) + ' ON pc' + str(
                        pc_number) + '.id = pc' + str(pc_number - 1) + '.parent_id '
                    tmp_str = " ,COALESCE(pc" + str(pc_number) + ".name, 'No asignado') "
                    result_categ = tmp_str + result_categ
                if order_number > 3:
                    order_by += ' , ' + str(order_number)
            level_name_dict[almacen] = level_names

            query_ids = ("""
                SELECT
                    pp.id as "ID"
                    ,pp.default_code as "Codigo Producto"
                    """ + result_categ + """
                FROM
                    product_product pp
                    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    """ + join_categ + """
                WHERE
                    pp.id in
                    (SELECT
                        sm.product_id
                    FROM
                        stock_move sm
                    WHERE
                        sm.state = 'done'
                        AND (sm.location_id = """ + str(almacen) + """
                        )
                        """ + filtro_productos + """
                    GROUP BY 1)
                """ + order_by + """
            """)
            _logger.debug("\nQUERY:\n%s\n", query_ids)


            self.env.cr.execute(query_ids)

            # se obtienen los productos q han tenido movimientos en el stock actual
            product_categories = [j for j in self.env.cr.fetchall()]
            product_categories_dict[almacen] = product_categories
            if fuente == 'so' or fuente == 'both':

                for producto in product_categories:
                    temp_list = []
                    query = ("""
                       SELECT
                            pp.id as "ID",
                            pp.default_code as "Producto"
                            ,pt.name
                            ,sol.salesman_id as vendedor_id
                            ,pu.name as "Unidad de Medida"
                            ,SUM(COALESCE(sm.product_qty, 0.0)) as "Cantidad"
                            ,SUM(COALESCE(sm.product_qty, 0.0)*COALESCE(sm.price_unit, 0.0))/SUM(COALESCE(sm.product_qty, 1)) as "Precio de Costo"
                            ,SUM(sol.price_unit*COALESCE(sm.product_qty, 0.0))/SUM(COALESCE(sm.product_qty, 1)) as "Precio Unitario Promedio"
                            ,SUM(COALESCE(sm.product_qty, 0.0)*sol.price_unit) as "Venta Bruta"
                            ,SUM(COALESCE(sm.product_qty, 0.0)*sol.price_unit*0.13) as "IVA Debito"
                            ,SUM(COALESCE(sm.product_qty, 0.0)*sol.price_unit*0.87) as "Venta Neta"
                            ,SUM(COALESCE(sm.product_qty, 0.0)*COALESCE(sm.price_unit, 0.0)) as "Costo Total"
                            ,SUM(COALESCE(sm.product_qty, 0.0)*sol.price_unit*0.87)-SUM(COALESCE(sm.product_qty, 0.0)*COALESCE(sm.price_unit, 0.0)) as "Margen de Ganancia"
                            ,CASE 
                                WHEN SUM(COALESCE(sm.product_qty, 0.0)*sol.price_unit*0.87) != 0 THEN
                                    100*(SUM(COALESCE(sm.product_qty, 0.0)*sol.price_unit*0.87)-SUM(COALESCE(sm.product_qty, 0.0)*COALESCE(sm.price_unit, 0.0)))/SUM(COALESCE(sm.product_qty, 1)*sol.price_unit*0.87)
                                ELSE 0
                            END as "%"
                        FROM
                            sale_order_line sol
                            join product_product pp on pp.id=sol.product_id
                            JOIN sale_order so ON so.id = sol.order_id
                            JOIN stock_move sm ON sm.sale_line_id = sol.id
                            INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
                            INNER JOIN uom_uom pu ON pu.id = pt.uom_id
                            JOIN stock_picking sp ON sp.id=sm.picking_id
                        WHERE
                            
                            so.state not in ('draft', 'cancel') and 
                            sm.state not in ('draft', 'cancel') 
                            """+str(filtro_almacen)+"""
                            AND pp.id = """+str(producto[0])+"""
                            """ + str(filtro_fechas_po) + """
                        GROUP BY 1, 2, 3, 4, 5
                    """)
                    _logger.debug("\nQUERY:\n%s\n", query)
                    self.env.cr.execute(query)
                    detalle_utilidad = [j for j in self.env.cr.fetchall()]

                    if detalle_utilidad:
                        if data['form']['as_consolidado']:
                            #creando previamente la estructura
                            for detalle_row in detalle_utilidad:
                                temp_dict = {}
                                vendedor_id = 1
                                if not vendedor_id in vendedores_dict:
                                    vendedores_dict[vendedor_id] = temp_dict

                            for detalle_row in detalle_utilidad:

                                vendedor_id = 1

                                if vendedor_id in vendedores_dict:
                                    for key_dict, values_dict in vendedores_dict.items():
                                        if key_dict == vendedor_id:
                                            if almacen in values_dict:
                                                vendedores_dict[vendedor_id][almacen].append(detalle_row)
                                            else:
                                                temp_list = []
                                                temp_list.append(detalle_row)
                                                vendedores_dict[vendedor_id][almacen] = temp_list
                        else:
                            #creando previamente la estructura
                            for detalle_row in detalle_utilidad:
                                temp_dict = {}
                                vendedor_id = detalle_row[3]
                                if not vendedor_id in vendedores_dict:
                                    vendedores_dict[vendedor_id] = temp_dict

                            for detalle_row in detalle_utilidad:

                                vendedor_id = detalle_row[3]

                                if vendedor_id in vendedores_dict:
                                    for key_dict, values_dict in vendedores_dict.items():
                                        if key_dict == vendedor_id:
                                            if almacen in values_dict:
                                                vendedores_dict[vendedor_id][almacen].append(detalle_row)
                                            else:
                                                temp_list = []
                                                temp_list.append(detalle_row)
                                                vendedores_dict[vendedor_id][almacen] = temp_list
        list_ids = []
        lista_ini_dict = level_name_dict.items()
        for key_dict, values_dict in vendedores_dict.items():  # iterando por vendedor
            level_name_dict_aux = {}
            for i in lista_ini_dict:
                level_name_dict_aux[i[0]] = i[1]

            filas_totales_almacen = {}
            almacen_cantidad = {}
            almacen_precio_costo = {}
            almacen_precio_unitario_venta = {}
            almacen_venta_bruta = {}
            almacen_iva_debito = {}
            almacen_importe = {}
            almacen_costo_compra = {}
            almacen_margen_ganancia = {}
            for key_almacen, value_det_utilidades in values_dict.items():  # iterando por almacen
                filas += 1

                if key_almacen not in almacen_cantidad: almacen_cantidad[key_almacen] = 0
                if key_almacen not in almacen_precio_costo: almacen_precio_costo[key_almacen] = 0
                if key_almacen not in almacen_precio_unitario_venta: almacen_precio_unitario_venta[key_almacen] = 0
                if key_almacen not in almacen_venta_bruta: almacen_venta_bruta[key_almacen] = 0
                if key_almacen not in almacen_iva_debito: almacen_iva_debito[key_almacen] = 0
                if key_almacen not in almacen_importe: almacen_importe[key_almacen] = 0
                if key_almacen not in almacen_costo_compra: almacen_costo_compra[key_almacen] = 0
                if key_almacen not in almacen_margen_ganancia: almacen_margen_ganancia[key_almacen] = 0

                if data['form']['as_consolidado']:
                    sheet.merge_range('A' + str(filas + 1) + ':B' + str(filas + 1), 'CONSOLIDADO', titulo2)
                else:
                    vendedor_obj = self.env['res.users'].search([('id', '=', key_dict)])
                    if key_dict not in list_ids:
                        sheet.merge_range(filas, 0, filas, 1, vendedor_obj.display_name, titulo2)
                        list_ids.append(key_dict)

                filas_totales_categ = {}
                total_cantidad = {}
                total_precio_costo = {}
                total_precio_unitario_venta = {}
                total_venta_bruta = {}
                total_iva_debito = {}
                total_importe = {}
                total_costo_compra = {}
                total_margen_ganancia = {}

                # si encontramos movimientos pasamos a la impresion
                for producto in product_categories_dict[key_almacen]:
                    for detalle_utilidad in value_det_utilidades:
                        if producto[0] == detalle_utilidad[0]:  # si para el producto actual exite el detalle de utilidad para el almacen y vendedor actual
                            posicion = ''
                            blanco = ''
                            # insertando el almacen inicialmente
                            if key_almacen not in filas_totales_almacen:
                                # filas += 1
                                filas_totales_almacen[key_almacen] = filas

                                id_almacen = int(str(key_almacen).replace('(', '').replace(')', ''))
                                almacen_obj = self.env['stock.location'].search([('id', '=', id_almacen)], limit=1)
                                sheet.merge_range(filas, 0, filas, 1, almacen_obj.name, titulo2)
                            for x in range(data['form']['as_categ_levels']):
                                level = x + 2
                                posicion += producto[level] + ','
                                if level > 2: blanco += '      '
                                if producto[level] != level_name_dict_aux[key_almacen][level]:
                                    filas += 1
                                    filas_totales_categ[posicion] = filas
                                    sheet.set_row(filas, None, None, {'level': level - 1})
                                    sheet.merge_range('A' + str(filas + 1) + ':B' + str(filas + 1),
                                                      blanco + producto[level],
                                                      letter2)
                                    level_name_dict_aux[key_almacen][level] = producto[level]


                            # for detalle in detalle_utilidad:
                            filas += 1
                            
                            sheet.write(filas,0, str(detalle_utilidad[1]) + " -- " + detalle_utilidad[2]) # str para funcionar producto - name_template
                            sheet.write(filas, 1, detalle_utilidad[4],number_left)  # unidad medida
                            sheet.write(filas, 2, detalle_utilidad[5], number_right)  # cantidad
                            sheet.write(filas, 3, detalle_utilidad[6], number_right)  # precio costo
                            sheet.write(filas, 4, detalle_utilidad[7], number_right)  # precio unitario promedio
                            sheet.write(filas, 5, detalle_utilidad[8], number_right)  # venta bruta
                            sheet.write(filas, 6, detalle_utilidad[9], number_right)  # iva debito
                            sheet.write(filas, 7, detalle_utilidad[10],number_right)  # venta neta
                            sheet.write(filas, 8, detalle_utilidad[11],number_right)  # costo total
                            sheet.write(filas, 9, detalle_utilidad[12],number_right)  # margen ganancia
                            sheet.write(filas, 10, detalle_utilidad[13],number_right)  # %
                            sheet.set_row(filas, None, None, {'level': data['form']['as_categ_levels'] + 1})

                            # TOTALES POR CATEGORIA
                            posicion = ''
                            for x in range(data['form']['as_categ_levels']):
                                level = x + 2
                                posicion += producto[level] + ','

                                if posicion not in total_cantidad: total_cantidad[posicion] = 0
                                total_cantidad[posicion] += detalle_utilidad[5]

                                if posicion not in total_precio_costo: total_precio_costo[posicion] = 0
                                total_precio_costo[posicion] += detalle_utilidad[6]

                                if posicion not in total_precio_unitario_venta: total_precio_unitario_venta[posicion] = 0
                                total_precio_unitario_venta[posicion] += detalle_utilidad[7]

                                if posicion not in total_venta_bruta: total_venta_bruta[posicion] = 0
                                total_venta_bruta[posicion] += detalle_utilidad[8]

                                if posicion not in total_iva_debito: total_iva_debito[posicion] = 0
                                total_iva_debito[posicion] += detalle_utilidad[9]

                                if posicion not in total_importe: total_importe[posicion] = 0
                                total_importe[posicion] += detalle_utilidad[10]

                                if posicion not in total_costo_compra: total_costo_compra[posicion] = 0
                                total_costo_compra[posicion] += detalle_utilidad[11]

                                if posicion not in total_margen_ganancia: total_margen_ganancia[posicion] = 0
                                total_margen_ganancia[posicion] += detalle_utilidad[12]

                            # TOTALES POR ALMACEN
                            almacen_cantidad[key_almacen] += detalle_utilidad[5]

                            almacen_precio_unitario_venta[key_almacen] += detalle_utilidad[7]
                            
                            almacen_precio_costo[key_almacen] += detalle_utilidad[6]

                            almacen_venta_bruta[key_almacen] += detalle_utilidad[8]

                            almacen_iva_debito[key_almacen] += detalle_utilidad[9]

                            almacen_importe[key_almacen] += detalle_utilidad[10]

                            almacen_costo_compra[key_almacen] += detalle_utilidad[11]

                            almacen_margen_ganancia[key_almacen] += detalle_utilidad[12]

                            for line in filas_totales_categ:
                                sheet.write(filas_totales_categ[line], 2, total_cantidad[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 3, total_precio_costo[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 4, total_precio_unitario_venta[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 5, total_venta_bruta[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 6, total_iva_debito[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 7, total_importe[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 8, total_costo_compra[line], number_right_bold)
                                sheet.write(filas_totales_categ[line], 9, total_margen_ganancia[line],
                                            number_right_bold)
                                sheet.write(filas_totales_categ[line], 10,
                                            '=100*J' + str(filas_totales_categ[line] + 1) + '/H' + str(
                                                filas_totales_categ[line] + 1), number_right_bold)

                for i in lista_ini_dict:
                    for k, v in i[1].items():
                        i[1][k] = ''
                    level_name_dict[i[0]] = i[1]

            for line1 in filas_totales_almacen:
                sheet.write(filas_totales_almacen[line1], 2, almacen_cantidad[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 3, almacen_precio_costo[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 4, almacen_precio_unitario_venta[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 5, almacen_venta_bruta[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 6, almacen_iva_debito[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 7, almacen_importe[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 8, almacen_costo_compra[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 9, almacen_margen_ganancia[line1], number_right_bold)
                sheet.write(filas_totales_almacen[line1], 10,
                            '=100*J' + str(filas_totales_almacen[line1] + 1) + '/H' + str(
                                filas_totales_almacen[line1] + 1), number_right_bold)