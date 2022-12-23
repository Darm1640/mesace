# # -*- coding: utf-8 -*-
import time
from openpyxl.styles import Alignment
import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
from io import BytesIO
from odoo.tools.image import image_data_uri
import math
import locale
from urllib.request import urlopen
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class as_resumen_ventas_gestion(models.AbstractModel):
    _name = 'report.as_bo_sale_route.as_resumen_ventas_gestion_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Resumen de Vnetas por Gestion')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', })
        number_subtitulos=workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True })
        totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  'bold':True })
        totales_valores = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  })
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True,})
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#A9A9A9'})
        color_subts=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#F0F8FF'})

        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(True)
        totales_Azul = workbook.add_format({'font_size': 12, 'align': 'right', 'bold':True,'bg_color':'#F0F8FF'})
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        sheet.set_column('A:N',10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',30, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',25, letter1)
        sheet.set_column('D:D',25, letter1)
        sheet.set_column('E:E',25, letter1)
        sheet.set_column('F:F',25, letter1)
        sheet.set_column('G:G',25, letter1)
        sheet.set_column('H:H',25, letter1)
        sheet.set_column('I:I',25, letter1)
        sheet.set_column('J:J',25, letter1)
        sheet.set_column('K:K',25, letter1)
        sheet.set_column('L:L',25, letter1)
        sheet.set_column('M:M',25, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:M5', 'RESUMEN DE VENTAS POR GESTION', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['fecha_inicial']), '%Y').strftime('%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.38, 'y_scale': 0.17})
        # sheet.write(7, 0, 'Tipo de Producto', titulo4)
        # sheet.merge_range('B8:C8', self.tipo_producto(data['form']), titulo3)
        sheet.write(8, 0, 'Usuario', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(9, 0, 'Almacen', titulo4)
        sheet.write(9, 1, self.nombre_almacen(data['form']),titulo3)
        sheet.write(7, 10, 'Clientes: ', titulo4)
        sheet.merge_range('L8:M8', self.nombre_cliente(data['form']), titulo3)
        sheet.write(8, 10, 'Divisa: ', titulo4)
        sheet.write(9, 10, 'Fecha de impresion: ', titulo4)
        sheet.write(9, 11, fecha, titulo3)
        sheet.merge_range('A6:M6', ' GESTION['+ fecha_inicial +']', tituloAzul)
        sheet.write(0, 10, 'NIT: ', titulo3) 
        sheet.write(1, 10, 'DIRECCION: ', titulo3) 
        sheet.write(2, 10, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('L1:M1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('L2:M2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('L3:M3', str(self.env.user.company_id.phone), titulo3derecha) 
        
        sheet.write(11, 0, 'CLIENTE', titulo2) 
        sheet.write(11, 1, 'ENERO', titulo2) 
        sheet.write(11, 2, 'FEBRERO', titulo2) 
        sheet.write(11, 3, 'MARZO', titulo2)
        sheet.write(11, 4, 'ABRIL', titulo2)
        sheet.write(11, 5, 'MAYO', titulo2)
        sheet.write(11, 6, 'JUNIO', titulo2)
        sheet.write(11, 7, 'JULIO', titulo2)
        sheet.write(11, 8, 'AGOSTO', titulo2)
        sheet.write(11, 9, 'SEPTIEMBRE', titulo2)
        sheet.write(11, 10, 'OCTUBRE', titulo2)
        sheet.write(11, 11, 'NOVIEMBRE', titulo2)
        sheet.write(11, 12, 'DICIEMBRE', titulo2)
        filas = 12
        columna=0
        id_del_almacen=0
        filas_total_mes=14
        dict_clientes = []
        dict_aux = []
        dict_almacen = []
        if data['form']['nombre_cliente']:
            for ids in data['form']['nombre_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND rp.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''
        #filtro del wizard tipo de producto
        # if data['form']['as_tipo_producto']:
        #     filtro_producto = """AND pt.type = '"""+str(data['form']['as_tipo_producto'])+"""'"""
        # else:
        #     filtro_producto = ''
        #filtro del wizard almacen
        
        if data['form']['as_almacen']:
            for line in data['form']['as_almacen']:
                dict_almacen.append('('+str(line)+')')
                dict_aux.append(line)
                id_del_almacen=dict_aux.append(line)
        else:
            almacenes_internos = self.env['stock.location'].search([('usage', '=', 'internal')])
            for line in almacenes_internos:
                dict_almacen.append('('+str(line.id)+')')
                dict_aux.append(line.id)
                id_del_almacen=dict_aux.append(line.id)
        
        #ALMACENES
        for almacen in dict_almacen:
            id_almacen = int(str(almacen).replace('(','').replace(')',''))
            almacen_obj = self.env['stock.location'].search([('id', '=', id_almacen),('usage','=','internal')])
            nombre_almacen=almacen_obj.name

            sheet.merge_range('A'+str(filas+1)+':M'+str(filas+1), nombre_almacen, color_cabecera_plomo)
            sheet.merge_range('A'+str(filas+2)+':M'+str(filas+2), 'ALMACENABLE', color_subts)
            filas+=2
            #1 consulta trayendo los clientes
            #verificar lña consulta cuabndo son el mismo cliente repetido
            consulta_cliente_servicio= ("""
            select 
                DISTINCT ON (rp.name) rp.name,
                rp.id
                from sale_order_line as sol
                left join sale_order as so on so.id=sol.order_id
                left join res_partner as rp on rp.id=so.partner_id
                left join product_product as pp on pp.id=sol.product_id
                left join product_template as pt on pt.id=pp.product_tmpl_id
                left join stock_picking sp on sp.origin=so.name
                where pt.type='product' AND so.state='sale'
            """+str(filtro_clientes)+""" AND sp.location_id =  '"""+str(id_almacen)+"""'
            """)
            self.env.cr.execute(consulta_cliente_servicio)
            querys_almacenable = [j for j in self.env.cr.fetchall()] 
            monto_servicio=0.00
            monto_service=0.00
            columna_servicio=1
            dict_productos={
                1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0,
                7:0.0, 8:0.0, 9:0.0, 10:0.0, 11:0.0, 12:0.0
                } #diccionario
            for linea_servicio in querys_almacenable:
                sheet.write(filas, 0, linea_servicio[0], number_left)
                #crear ciclo lista que recorra del 1 al 12
                lista_servicio=['01','02','03','04','05','06','07','08','09','10','11','12']
                for i in lista_servicio:
                    monto_servicio=self.productos(i, linea_servicio[1],  data['form']['fecha_inicial'], id_almacen) #pasarle mes y pasarle cliente
                    if monto_servicio != None:
                        sheet.write(filas, columna_servicio, monto_servicio, totales_valores) #
                    else:
                        sheet.write(filas, columna_servicio, '0.00', totales_valores) #
                    if monto_servicio != None:
                        dict_productos[int(i)]+=monto_servicio
                    columna_servicio+=1
                filas_total_mes+=1
                columna_servicio=1
                filas+=1          
            sheet.write(filas, 0, 'TOTAL', totales) #
            columna_servicio=1
            indice_dos=[1,2,3,4,5,6,7,8,9,10,11,12]
            for k in indice_dos:
                sheet.write(filas, columna_servicio, dict_productos[k], totales)
                columna_servicio+=1
            filas+=2
            sheet.merge_range('A'+str(filas+1)+':M'+str(filas+1), 'SERVICIO', color_subts)
            filas+=1
            
            consulta_service_reporte= ("""
            select 
                DISTINCT ON (rp.name) rp.name,
                rp.id,
                so.id
                from sale_order_line as sol
                left join sale_order as so on so.id=sol.order_id
                left join res_partner as rp on rp.id=so.partner_id
                left join product_product as pp on pp.id=sol.product_id
                left join product_template as pt on pt.id=pp.product_tmpl_id
                left join stock_picking sp on sp.origin=so.name
                where pt.type='product' AND so.state='sale'
            """+str(filtro_clientes)+""" AND sp.location_id =  '"""+str(id_almacen)+"""'
            """)
            self.env.cr.execute(consulta_service_reporte)
            querys_servicio = [j for j in self.env.cr.fetchall()] 
            monto_service=0.00
            columna_servicio=1
            dict_services={
                1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0,
                7:0.0, 8:0.0, 9:0.0, 10:0.0, 11:0.0, 12:0.0
                } #diccionario
            for linea_service in querys_servicio:
                sheet.write(filas, 0, linea_service[0], number_left)
                #crear ciclo lista que recorra del 1 al 12
                lista_service=['01','02','03','04','05','06','07','08','09','10','11','12']
                for i in lista_service:
                    # monto_service=self.servicios(i, linea_service[1],data['form']['as_divisas'],data['form']['fecha_inicial']) #pasarle mes y pasarle cliente
                    monto_service=self.servicios(i, linea_service[1],data['form']['fecha_inicial']) #pasarle mes y pasarle cliente
                    if monto_service != None:
                        sheet.write(filas, columna_servicio, monto_service, totales_valores) #
                    else:
                        sheet.write(filas, columna_servicio, '0.00', totales_valores) #
                    if monto_service != None:
                        dict_services[int(i)]+=monto_service
                    columna_servicio+=1
                filas_total_mes+=1
                columna_servicio=1
                filas+=1          
            sheet.write(filas, 0, 'TOTAL', totales) #
            columna_servicio=1
            indice_dos=[1,2,3,4,5,6,7,8,9,10,11,12]
            for k in indice_dos:
                sheet.write(filas, columna_servicio, dict_services[k], totales)
                columna_servicio+=1
            filas+=2
            
        
        
    # def equipos(self, mes, cliente,  fecha_inicial, id_almacen):
    #     consulta_mes_cliente=("""
    #     select 
        
    #     rp.id,
    #     sum(sol.price_total) as "suma total de las ventas",
    #     so.id
        
    #     from sale_order_line as sol
    #     left join sale_order as so on so.id=sol.order_id
    #     left join res_partner as rp on rp.id=so.partner_id
    #     left join product_product as pp on pp.id=sol.product_id
    #     left join product_template as pt on pt.id=pp.product_tmpl_id
    #     left join stock_picking sp on sp.origin=so.name
        
    #     where pt.type='product' AND so.state='sale' AND to_char(so.date_order, 'MM') = '"""+str(mes)+ """'
    #     AND rp.id= '"""+str(cliente)+"""'   AND to_char(so.date_order, 'YY') = '"""+str(fecha_inicial)+ """' AND sp.location_id =  '"""+str(id_almacen)+"""'
    #     GROUP BY rp.id, so.id
    #     """)
    #     self.env.cr.execute(consulta_mes_cliente)
    #     querys = [j for j in self.env.cr.fetchall()]
    #     monto=0.00
    #     for linea in querys: 
    #         id_invoice = self.env['sale.order'].search([('id','=',linea[2])])
    #         if id_invoice:
    #             monto=linea[1]
    #             # if id_invoice.currency_id.name == 'USD':
    #             #     monto=round((linea[1]/0.143678000000),1)
    #             # else:
    #             #     monto=linea[1]
    #     return monto
    
    def productos(self, mes, cliente, fecha_inicial, id_almacen):
        consulta_mes_cliente=("""
        select 
        
        sum(sol.price_total)
        
        from sale_order_line as sol
        left join sale_order as so on so.id=sol.order_id
        left join res_partner as rp on rp.id=so.partner_id
        left join product_product as pp on pp.id=sol.product_id
        left join product_template as pt on pt.id=pp.product_tmpl_id
        left join stock_picking sp on sp.origin=so.name
        where pt.type='product' AND so.state='sale' AND to_char(so.date_order, 'MM') = '"""+str(mes)+ """'
        AND rp.id= '"""+str(cliente)+"""'  AND to_char(so.date_order, 'YYYY') = '"""+str(fecha_inicial)+ """' AND sp.location_id =  '"""+str(id_almacen)+"""'
        """)
        self.env.cr.execute(consulta_mes_cliente)
        querys = [j for j in self.env.cr.fetchall()]
        monto=0.00
        for linea in querys: 
            monto=linea[0]
                # if id_invoice.currency_id.name == 'USD':
                #     monto=round((linea[1]/0.143678000000),1)
                # else:
                #     monto=linea[1]
        return monto
    
    def servicios(self, mes, cliente,fecha_inicial):
        consulta_mes_cliente_servicio=("""
        select 
        sum(sol.price_total)

        from sale_order_line as sol
        left join sale_order as so on so.id=sol.order_id
        left join res_partner as rp on rp.id=so.partner_id
        left join product_product as pp on pp.id=sol.product_id
        left join product_template as pt on pt.id=pp.product_tmpl_id
        
        
        where pt.type='service' AND so.state='sale'  AND to_char(so.date_order, 'MM') = '"""+str(mes)+ """'
        AND rp.id= '"""+str(cliente)+"""' AND to_char(so.date_order, 'YYYY') = '"""+str(fecha_inicial)+ """'
        """)
        # AND so.currency_id = '"""+str(divisa)+"""'
        self.env.cr.execute(consulta_mes_cliente_servicio)
        querys = [j for j in self.env.cr.fetchall()]
        monto=0.00
        for linea in querys: 
            # id_invoice = self.env['sale.order'].search([('id','=',linea[2])])
            # if id_invoice:
            monto=linea[0]
            #     if id_invoice.currency_id.name == 'USD':
            #         monto=round((linea[1]/0.143678000000),1)
            #     else:
            #         monto=linea[1]
        return monto
     
    # def tipo_producto(self,data):
    #     filtro=''
    #     if data['as_tipo_producto']:
    #         if data['as_tipo_producto']=='product':
    #             filtro='Almacenable'
    #         if data['as_tipo_producto']=='service':
    #             filtro='Servicio'
    #         if data['as_tipo_producto']=='consu':
    #             filtro='Consumible'
    #     else:
    #         filtro='Almacenable, Servicio, Consumible'
    #     return filtro
    
    def nombre_almacen(self,data):
        dict_aux = []
        dict_almacen = []
        almacen=data['as_almacen']
        if almacen:
            for line in almacen:
                dict_almacen.append('('+str(line)+')')
                dict_aux.append(line)
        filtro_almacenes_name = 'Todos'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name
    
    def nombre_cliente(self,data):
        dict_aux = []
        almacen=data['nombre_cliente']
        if almacen:
            for line in almacen:
                dict_aux.append(line)
        filtro_almacenes_name = 'Varios'
        for y in dict_aux:
            almacen_obj = self.env['res.partner'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['res.partner'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name