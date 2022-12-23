# # -*- coding: utf-8 -*-
from io import BytesIO
from collections import defaultdict
from datetime import date, datetime, time
from operator import attrgetter
from xmlrpc.client import MAXINT
import logging
from odoo.tools.translate import _
import time
from odoo.exceptions import UserError, ValidationError
from time import mktime
from odoo.tools.image import image_data_uri
import locale
from odoo.exceptions import UserError
from urllib.request import urlopen
import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
from xlsxwriter.workbook import Workbook
_logger = logging.getLogger(__name__)

class as_salidas_inventario(models.AbstractModel):
    _name = 'report.as_bo_stock.as_salidas_inventario_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines): 
        lista = []
        lista2 = []
        estado = ''

        consulta = "and (stock_move.date::TIMESTAMP+ '-4 hr')::date >= '""" + str(data['form']['start_date']) + "' AND (stock_move.date::TIMESTAMP+ '-4 hr')::date <= '" + str(data['form']['end_date']) + "'"

        dic_location = []
        # Consulta para campo de tipo m2o
        # if data['form']['location']:
        #      consulta += " AND stock_move.location_id = " + str(self.location.id)
        
        if data['form']['location_m2m']:
            for id in data['form']['location_m2m']:
                dic_location.append(id)
            consulta += " AND stock_move.location_id in " + str(dic_location).replace('[','(').replace(']',')')
        if data['form']['product']:
            consulta += " AND stock_move.product_id = " + str(data['form']['product'])
        if data['form']['estado_salidas']:
            consulta += " AND stock_move.state = '" + str(data['form']['estado_salidas'])+"'"
        consulta += " ORDER BY stock_move.date ASC"
        consulta_general=("""
            SELECT
            stock_move.id
            FROM stock_move
            JOIN stock_picking_type ON stock_picking_type.id=stock_move.picking_type_id
            INNER JOIN stock_picking sp ON sp.id = stock_move.picking_id
            WHERE picking_id IS NOT NULL AND stock_picking_type.code IN ('outgoing','internal')
            """+ consulta)
        self.env.cr.execute(consulta_general) 
        move_ids = [x[0] for x in self.env.cr.fetchall()]
        for stock_move in self.env['stock.move'].browse(move_ids):
            estado = self._traduccion_estado(stock_move.state)
            fecha_actual = (datetime.strptime(str(stock_move.picking_id.date), '%Y-%m-%d %H:%M:%S') - timedelta(hours=4)).strftime('%d/%m/%Y') if str(stock_move.picking_id.date) else '-'
            dic = {
                'fecha' : fecha_actual,
                'nota_ingreso' : stock_move.picking_id.name,
                'nota_venta' : stock_move.picking_id.origin,
                'cliente': stock_move.picking_id.partner_id.name,
                'referencia_interna': stock_move.product_id.default_code,
                'producto': stock_move.product_id.display_name,
                'cantidad': stock_move.product_qty,
                'costo': stock_move.price_unit,
                'total': (stock_move.product_qty * stock_move.price_unit),
                'categoria_producto': (stock_move.product_id.product_tmpl_id.categ_id.name),
                'estado': estado,
                'ubicacion_origen'  : stock_move.picking_id.location_id.name,
                'ubicacion_destino' : stock_move.picking_id.location_dest_id.name,
            }
            if 'outgoing' in stock_move.picking_id.picking_type_id.code:
                lista.append(dic)
            else:
                lista2.append(dic)
        
        sheet = workbook.add_worksheet('SALIDAS DE INVENTARIO')
        #Definiciones generales del archivo, formatos, titulos, hojas de trabajo
        titulo1 = workbook.add_format({'font_size': 15,'font_name': 'Lucida Sans', 'align': 'center','bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00'})
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter4C = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True,'color': '#000000','bg_color': '#F4F5F5','font_name': 'Lucida Sans', })
        letter5 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)


        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',20, letter1)
        sheet.set_column('B:B',20, letter1)
        sheet.set_column('C:C',20, letter1)
        sheet.set_column('D:D',20, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',20, letter1)
        sheet.set_column('H:H',20, letter1)
        sheet.set_column('I:I',25, letter1)
        sheet.set_column('J:J',20, letter1)
        sheet.set_column('K:K',20, letter1)
        sheet.set_column('L:L',20, letter1)
        sheet.set_column('M:M',22, letter1)
        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A4:M5', 'SALIDAS DE INVENTARIO', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(data['form']['start_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(data['form']['end_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:B4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})
        sheet.merge_range('A6:M6', fecha_inicial +' - '+ fecha_final, titulo2)
        sheet.merge_range('K1:L1', 'NIT: ', titulo3) 
        sheet.merge_range('K2:L2', 'DIRECCION: ', titulo3) 
        sheet.merge_range('K3:L3', 'CELULAR, TELEFONO: ', titulo3)
        sheet.write(8, 11, 'Fecha de impresion: ', titulo4)
        sheet.write(8 ,12, fecha, titulo3) 
        sheet.write(7, 0, 'Usuario:', titulo4)
        sheet.merge_range('B8:C8', str(self.env.user.partner_id.name), titulo3)
        sheet.write(8, 0, 'Almacen:', titulo4)
        sheet.write(8, 1, 'VARIOS', titulo3)
        sheet.write(7, 11, 'Productos: ', titulo4)
        sheet.write(7 ,12, 'Todos', titulo3)
        filastitulo1=10
        filastitle1=10
        sheet.write(filastitulo1, 0, 'Fecha', tituloAzul)  
        sheet.write(filastitulo1, 1, 'Nota de Ingreso', tituloAzul)   
        sheet.write(filastitulo1, 2, 'Nota de Venta', tituloAzul)   
        sheet.write(filastitulo1, 3, 'Cliente', tituloAzul)   
        sheet.write(filastitulo1, 4, 'Referencia Int.', tituloAzul)  
        sheet.write(filastitulo1, 5, 'Producto', tituloAzul)   
        sheet.write(filastitulo1, 6, 'Cantidad', tituloAzul)    
        sheet.write(filastitulo1, 7, 'Costo', tituloAzul)  
        sheet.write(filastitulo1, 8, 'Total', tituloAzul)   
        sheet.write(filastitulo1, 9, 'Categoria Producto', tituloAzul)
        sheet.write(filastitulo1, 10, 'Estado', tituloAzul)
        sheet.write(filastitulo1, 11, 'Ubicacion de Origen', tituloAzul)
        sheet.write(filastitulo1, 12, 'Ubicacion de Destino', tituloAzul)
        sheet.freeze_panes(5, 0)  
        # Titulos, subtitulos, filtros y campos del reporte HOJA DE CALCULO 2
        total_cantidad = 0.0
        total_compra = 0.0 
        for y in lista:
            filastitle1+=1
            sheet.write(filastitle1, 0, y['fecha'],number_right )
            sheet.write(filastitle1, 1, y['nota_ingreso'],number_left)
            sheet.write(filastitle1, 2, y['nota_venta'],number_right)
            sheet.write(filastitle1, 3, y['cliente'],number_left)
            sheet.write(filastitle1, 4, y['referencia_interna'] or 'S/C',number_right)
            sheet.write(filastitle1, 5, y['producto'],number_left)
            sheet.write(filastitle1, 6, y['cantidad'],number_right)
            sheet.write(filastitle1, 7, y['costo'] or 0.0,number_right)
            sheet.write(filastitle1, 8, y['total'],number_right)
            sheet.write(filastitle1, 9, y['categoria_producto'], number_left)
            sheet.write(filastitle1, 10, y['estado'], number_left)
            sheet.write(filastitle1, 11, y['ubicacion_origen'], number_left)
            sheet.write(filastitle1, 12, y['ubicacion_destino'], number_left)
            total_cantidad += y['cantidad']
            total_compra += y['total']
        filastitle1+=1
        sheet.merge_range('A'+str(filastitle1+1)+':F'+str(filastitle1+1), 'TOTAL', )
        sheet.write(filastitle1,6, total_cantidad, number_right)
        sheet.write(filastitle1,7, '', )
        sheet.write(filastitle1,8, total_compra, number_right)
        sheet.write(filastitle1,10, '', )
        


    def _traduccion_estado(self,estado_traducir):
        estado = ''
        if estado_traducir == 'draft':
            estado = 'Presupuesto borrador'
        if estado_traducir == 'cancel':
            estado = 'Cancelado'
        if estado_traducir == 'waiting':
            estado = 'Esperando otra operacion'
        if estado_traducir == 'confirmed':
            estado = 'Esperando Disponibilidad'
        if estado_traducir == 'partially_available':
            estado = 'Parcialmente disponible'
        if estado_traducir == 'assigned':
            estado = 'Listo para transferir'
        if estado_traducir == 'done':
            estado = 'Realizado'
        return estado
    def _total_cantidad(self):
             return self.total_cantidad

    def _gran_total(self):
             return self.gran_total

    def _get_report_values(self, docids, data=None):
        self.total_cantidad = 0.00
        self.gran_total = 0.00
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'fecha_actual' : self._fecha_actual(),
            'fecha_inicial' : self._fecha_inicial(data['form']),
            'fecha_final' : self._fecha_final(data['form']),
            'lista_salidas_inventarios' : self._lista_salidas_inventarios(data['form']),
            'total_cantidad' : self._total_cantidad(),
            'gran_total' : self._gran_total(),
        }

    def _fecha_actual(self):
        fecha_actual = time.strftime('%d-%m-%Y %H:%M:%S')
        struct_time_convert = time.strptime(fecha_actual, '%d-%m-%Y %H:%M:%S')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        date_time_convert = date_time_convert - timedelta(hours = 4)
        fecha_actual = date_time_convert.strftime('%d-%m-%Y %H:%M:%S')
        return fecha_actual

    def _fecha_inicial(self,filtros):
        fecha_inicial = filtros['start_date']
        struct_time_convert = time.strptime(fecha_inicial, '%Y-%m-%d')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        fecha_inicial = date_time_convert.strftime('%d-%m-%Y')
        return fecha_inicial

    def _fecha_final(self,filtros):
        fecha_final = filtros['end_date']
        struct_time_convert = time.strptime(fecha_final, '%Y-%m-%d')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        fecha_final = date_time_convert.strftime('%d-%m-%Y')
        return fecha_final


    def _lista_salidas_inventarios(self,filtros):

        lista = []
        estado = ''

        stock_picking_pool = self.env['stock.picking']
        if filtros['estado_salidas']:
            stock_picking_search = stock_picking_pool.search([('picking_type_id.code','=','outgoing'),('state','=',filtros['estado_salidas'])],order='date')
        else:
            stock_picking_search = stock_picking_pool.search([('picking_type_id.code','=','outgoing')],order='date')
        for stock_picking in stock_picking_search:
            stock_move_pool = self.env['stock.move']
            if filtros['location']:
                if filtros['product']:
                    stock_move_search = stock_move_pool.search([('location_id','=',filtros['location'][0]),('picking_id','=',stock_picking.id),('product_id','=',filtros['product'][0])])
                else:
                    stock_move_search = stock_move_pool.search([('location_id','=',filtros['location'][0]),('picking_id','=',stock_picking.id)])
            else:
                if filtros['product']:
                    stock_move_search = stock_move_pool.search([('picking_id','=',stock_picking.id),('product_id','=',filtros['product'])])
                else:
                    stock_move_search = stock_move_pool.search([('picking_id','=',stock_picking.id)],order='date desc')

            #stock_mov = request.env['stock.move'].sudo().search([('sale_line_id', '=', celular)],limit=1)

                # fecha_actual = date_time_convert.strftime('%d-%m-%Y')
                for stock_move in stock_move_search:
                    fecha_actual = str(stock_move.date)
                    struct_time_convert = time.strptime(fecha_actual, '%Y-%m-%d %H:%M:%S')
                    date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
                    date_time_convert = date_time_convert - timedelta(hours = 4)
                    fecha_actual = date_time_convert.strftime('%Y-%m-%d')
                    if filtros['start_date'] <= fecha_actual <= filtros['end_date']:
                        self.total_cantidad += stock_move.product_qty
                        self.gran_total += (stock_move.product_qty * stock_move.price_unit)
                        estado = self._traduccion_estado(stock_picking.state)
                        dic = {
                            'fecha' : fecha_actual,
                            'nota_ingreso' : stock_move.picking_id.name,
                            'nota_venta' : stock_move.picking_id.origin,
                            'cliente': stock_move.picking_id.partner_id.name,
                            'referencia_interna': stock_move.product_id.default_code,
                            'producto': stock_move.product_id.display_name,
                            'cantidad': stock_move.product_qty,
                            'costo': stock_move.price_unit,
                            'total': (stock_move.product_qty * stock_move.price_unit),
                            'categoria_producto': (stock_move.product_id.product_tmpl_id.categ_id.name),
                            'estado': estado,
                            'ubicacion_origen'  : stock_move.picking_id.location_id.name,
                            'ubicacion_destino' : stock_move.picking_id.location_dest_id.name,
                            }
                        lista.append(dic)
            return lista

    def _total_cantidad(self):
        return self.total_cantidad

    def _gran_total(self):
        return self.gran_total 