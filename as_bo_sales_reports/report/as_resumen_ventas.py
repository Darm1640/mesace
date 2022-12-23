# # -*- coding: utf-8 -*-

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
_logger = logging.getLogger(__name__)

class as_sales_emit_excel(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.sales_sumary_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Resumen de ventas')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
        titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        
        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.0'})
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.0'})
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(True)

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',20, letter1)
        sheet.set_column('B:B',20, letter1)
        sheet.set_column('C:C',30, letter1)
        sheet.set_column('D:D',20, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',20, letter1)
        sheet.set_column('H:H',18, letter1)
        sheet.set_column('I:I',18, letter1)
        sheet.set_column('J:J',25, letter1)
        sheet.set_column('K:K',25, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:K5', 'RESUMEN DE VENTAS', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.467, 'y_scale': 0.165})
        sheet.write(7, 0, 'Usuario', titulo4)
        sheet.write(7, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(7, 9, 'Fecha de impresion: ', titulo4)
        sheet.write(7, 10, fecha, titulo3)

        sheet.write(0, 9, 'NIT: ', titulo3) 
        sheet.write(1, 9, 'DIRECCION: ', titulo3) 
        sheet.write(2, 9, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('A6:K6', fecha_inicial +' - '+ fecha_final, tituloAzul)
        sheet.write(10, 0, 'FECHA PEDIDO', titulo2)
        sheet.write(10, 1, 'No PEDIDO', titulo2)
        sheet.write(10, 2, 'CODIGO', titulo2)
        sheet.write(10, 3, 'COD CLIENTE', titulo2)
        sheet.write(10, 4, 'CLIENTE', titulo2)
        sheet.write(10, 5, 'RAZON SOCIAL', titulo2)
        sheet.write(10, 6, 'IMPORTE Bs.', titulo2)
        sheet.write(10, 7, 'FACTURADO', titulo2)
        sheet.write(10, 8, 'PAGO Bs.', titulo2)
        sheet.write(10, 9, 'SALDO Bs.', titulo2)
        sheet.write(10, 10, 'ESTADO', titulo2)
        filas = 11
        # Preparando variables para cada casod e consulta
        filtro_fechas_so = " AND (so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date BETWEEN '" + str(data['form']['start_date']) + "' AND '" + str(data['form']['end_date']) + "'"
        dict_vendedores = []
        if data['form']['as_vendedor']:
            for ids in data['form']['as_vendedor']:
                dict_vendedores.append(ids)
        if dict_vendedores:
            filtro_vendedores_so = "AND so.user_id in "+str(dict_vendedores).replace('[','(').replace(']',')')
        else:
            filtro_vendedores_so = ''
        dict_clientes = []
        if data['form']['as_cliente']:
            for ids in data['form']['as_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND cliente.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''
        dict_aux = []
        dict_almacen = []
        if data['form']['as_almacen']:
            for ids in data['form']['as_almacen']:
                dict_almacen.append(ids)
                dict_aux.append(ids)
        if dict_almacen:
            filtro_almacen = "WHERE sl.id in "+str(dict_almacen).replace('[','(').replace(']',')')
        else:
            filtro_almacen = ''
        sheet.write(8, 0, 'Almacen', titulo4)
        filtro_almacenes_name = 'VARIOS'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        sheet.merge_range('B9:C9', filtro_almacenes_name,titulo3)
        consulta_so = ("""
                SELECT
            sl.name as almacn,
            sl.id
            FROM stock_location AS sl
            """ + str(filtro_almacen) + """
            """)           
        self.env.cr.execute(consulta_so)
        k = [j for j in self.env.cr.fetchall()]
        for e in k: 
            consulta = ("""
                    SELECT
                to_char((so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date,'DD/MM/YYYY') AS fecha
                ,so.name as nro_pedido
                ,atp.name
                ,COALESCE(cliente.as_code, 'S/CODIGO')	as codigo_cliente
                ,COALESCE(cliente.name, 'S/NOMBRE')	AS nombre_cliente
                ,cliente.as_razon_social as razonkkkk
                ,so.amount_total as importe
                ,am.amount_total as facturado
                ,am.id as pago 
                ,am.amount_residual AS saldo
                ,CASE 
                    WHEN so.state = 'sale' THEN 'Pedido de venta'
                    WHEN so.state = 'done' THEN 'Realizado'
                    ELSE 'Devolucion'
                END as estado
                FROM sale_order AS so
                left JOIN res_users AS usuarios ON usuarios.id = so.user_id
                left join as_template_project atp ON atp.id=so.as_template_id
                left JOIN res_partner AS asesor ON asesor.id = usuarios.partner_id
                LEFT JOIN res_partner AS cliente ON cliente.id = so.partner_id
                left join account_move am on am.invoice_origin=so.name
                left join account_payment ap on ap.move_id=am.id
                left join account_move amove on amove.ref=am.name
                left join stock_picking sp on sp.origin=so.name
                left join stock_location sl on sp.location_id=sl.id
                WHERE so.state NOT IN ('cancel','draft')
                AND sl.id=""" + str(e[1]) + """
                """ + str(filtro_fechas_so) + """
                """ + str(filtro_vendedores_so) + """
                """ + str(filtro_clientes) + """
                ORDER BY so.name desc
                """)           
            self.env.cr.execute(consulta)
            ventas = [j for j in self.env.cr.fetchall()]
            if ventas != []:
                sheet.write(filas,0,e[0],number_right_bold)#fecha
                filas+=1
                importe=0.0
                facturado_total = 0.0
                pago_bs = 0.0
                saldo = 0.0
                for v in ventas:
                    sheet.write(filas,0,v[0],number_right)#fecha
                    sheet.write(filas,1,v[1],number_right)#pedido
                    sheet.write(filas,2,v[2],number_right)#codigo
                    sheet.write(filas,3,v[3],number_left)#code cliente
                    sheet.write(filas,4,v[4],number_left)#cliente
                    sheet.write(filas,5,v[5],number_left)#razon social
                    sheet.write(filas,6,v[6],number_right)#importe
                    importe+=v[6]
                    sheet.write(filas,7,v[7],number_right)#facturado
                    if v[7]==None:
                        facturado_total+=0.0
                    else:
                        facturado_total+=v[7]
                    id_invoice = self.env['account.move'].search([('id','=',v[8])])
                    diario=0.0
                    diario_str=''
                    if id_invoice:
                        for pagos in id_invoice.get_payment():
                            if pagos.currency_id.name == 'USD':
                                diario=round((pagos.amount/0.143678000000),1)
                                diario_str=str(diario)+'  '
                                pago_bs+=diario
                            else:
                                diario=pagos.amount
                                diario_str=str(diario)+'  '
                                pago_bs+=diario
                    sheet.write(filas,8,diario_str,number_right) # tipo de pago
                    sheet.write(filas,9,v[9],number_right)#saldo
                    if v[9]==None:
                        saldo+=0.0
                    else:
                        saldo+=v[9]
                    sheet.write(filas,10,v[10],number_left)#estad
                    filas+=1
                coltotal= 'A'+str(filas+1)+':'+'E'+str(filas+1)
                sheet.merge_range(coltotal, 'TOTALES',number_left) #fecha
                sheet.write(filas,6,importe,number_right)#total importe
                sheet.write(filas,7,facturado_total,number_right)#total FACTURADO
                sheet.write(filas,8,pago_bs,number_right)#total tipo de pago
                sheet.write(filas,9,saldo,number_right)#total saldo

