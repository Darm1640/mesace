# # -*- coding: utf-8 -*-

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
import string

class as_sales_emit_excel(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.sales_facturas_emitidas_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Facturas Emitidas')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
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
        totales_Azul = workbook.add_format({'font_size': 12, 'align': 'right', 'bold':True,'bg_color':'#F0F8FF'})
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        sheet.set_column('A:N',10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',15, letter1)
        sheet.set_column('B:B',15, letter1)
        sheet.set_column('C:C',30, letter1)
        sheet.set_column('D:D',15, letter1)
        sheet.set_column('E:E',15, letter1)
        sheet.set_column('F:F',15, letter1)
        sheet.set_column('G:G',15, letter1)
        sheet.set_column('H:H',18, letter1)
        sheet.set_column('I:I',18, letter1)
        sheet.set_column('J:J',20, letter1)
        sheet.set_column('K:K',20, letter1)
        sheet.set_column('L:L',20, letter1)
        sheet.set_column('M:M',20, letter1)
        sheet.set_column('N:N',20, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:N5', 'FACTURAS EMITIDAS', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        # fecha_año = datetime.strptime(str(data['form']['fecha_inicial']), '%Y').strftime('%Y')
        fecha_inicial = datetime.strptime(str(data['form']['fecha_inicial']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['fecha_final']), '%Y-%m-%d').strftime('%d/%m/%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.41, 'y_scale': 0.17})
        sheet.write(8, 0, 'Usuario', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(9, 0, 'Cliente', titulo4)
        sheet.write(9, 1, self.nombre_cliente(data['form']), titulo3)
        sheet.write(8, 12, 'Fecha de impresion: ', titulo4)
        sheet.write(8, 13, fecha, titulo3)
        sheet.write(9, 12, 'Vendedor ', titulo4)
        sheet.write(9, 13, self.nombre_asesor(data['form']), titulo3)
        sheet.merge_range('A6:N6', 'DE ['+ fecha_inicial +'] HASTA ['+ fecha_final+']', tituloAzul)
        # sheet.merge_range('A7:N7', ' GESTION['+ fecha_año +']', tituloAzul)
        sheet.write(0, 12, 'NIT: ', titulo3) 
        sheet.write(1, 12, 'DIRECCION: ', titulo3) 
        sheet.write(2, 12, 'CELULAR, TELEFONO:', titulo3)
        sheet.write(0, 13, str(self.env.user.company_id.vat), titulo3derecha) 
        sheet.write(1, 13, str(self.env.user.company_id.street), titulo3derecha) 
        sheet.write(2, 13, str(self.env.user.company_id.phone), titulo3derecha)
        
        sheet.write(10, 0, 'FECHA', titulo2) 
        sheet.write(10, 1, 'NUMERACION INTERNA', titulo2) 
        sheet.write(10, 2, 'UNIDAD DE NEGOCIO', titulo2)
        sheet.write(10, 3, 'NIT CLIENTE', titulo2)
        sheet.write(10, 4, 'RAZON SOCIAL', titulo2)
        sheet.write(10, 5, 'No AUTORIZACION', titulo2)
        sheet.write(10, 6, 'CODIGO DE CONTROL', titulo2)
        sheet.write(10, 7, 'IMPORTE BRUTO DE FACTURA AL CREDITO BS.', titulo2)
        sheet.write(10, 8, 'DESCUENTO CREDITO BS.', titulo2)
        sheet.write(10, 9, 'IMPORTE NETO DE FACTURA CREDITO BS.', titulo2)
        sheet.write(10, 10, 'No FACTURA', titulo2)
        sheet.write(10, 11, 'FECHA FACTURA', titulo2)
        sheet.write(10, 12, 'VENDEDOR', titulo2)
        sheet.write(10, 13, 'FORMA DE PAGO', titulo2)
        filas = 11
        # Preparando variables para cada casod e consulta
        dict_clientes = []
        if data['form']['nombre_cliente']:
            for ids in data['form']['nombre_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND rp.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''
        dict_vendedores = []
        if data['form']['asesor']:
            for ids in data['form']['asesor']:
                dict_vendedores.append(ids)
        if dict_vendedores:
            filtro_vendedores_so = "AND so.user_id in "+str(dict_vendedores).replace('[','(').replace(']',')')
        else:
            filtro_vendedores_so = ''

        consulta_product= ("""
            select 
            to_char((( so.date_order AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) as "fecha",
            am.name as "num interna",
            am.as_nit as "NIT",
            am.as_razon_social as "razon social",
            am.as_numero_autorizacion_compra as "n autoriza",
            am.as_codigo_control_compra as "codigo control", 
            so.amount_total as "importe bruto",
            am.amount_total as "importe neto",
            am.as_numero_factura_compra as "n factura",
            to_char(((am.invoice_date AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) as "fecha factura",
            rpartner.name as "vendedor",
            CASE 
                WHEN apt.name = 'Immediate Payment' THEN 'Pago inmediato'
                WHEN apt.name = '21 Days' THEN '21 Dias'
                WHEN apt.name = '15 Days' THEN '15 Dias'
                WHEN apt.name = '30 Days' THEN '30 Dias'
                WHEN apt.name = '45 Days' THEN '45 Dias'
                WHEN apt.name = '2 Months' THEN '2 Meses'
                WHEN apt.name = 'End of Following Month' THEN 'Fin de Mes Siguiente'
                WHEN apt.name = '30% Now, Balance 60 Days' THEN '30% Ahora, Balance 60 Días'
            END as "forma de pago",
            am.id,
            am.as_invoice_number
            from sale_order so
            left JOIN account_move as am on am.invoice_origin=so.name
            left join res_partner as rp on rp.id=am.partner_id
            left join account_payment_term apt on apt.id=so.payment_term_id
            left join res_users ru on ru.id=am.invoice_user_id
            left join res_partner rpartner on rpartner.id=ru.partner_id
            where
            am.move_type='out_invoice' AND (so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['fecha_inicial'])+ """'
            AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['fecha_final'])+ """'
            
            """+str(filtro_clientes)+"""
            """ + str(filtro_vendedores_so) + """
            ORDER BY so.date_order desc
            """)

        self.env.cr.execute(consulta_product)
        querys = [j for j in self.env.cr.fetchall()]
        cont=0
        total_omporte_bruto = 0.0
        total_descuento = 0.0 
        total_improte_neto_Facura = 0.0 
        
        for linea in querys:            
            
            sheet.write(filas, 0, linea[0], number_right) #fecha 
            sheet.write(filas, 1, linea[1], number_right) #num int
            diario=''
            words=''
            busines = self.env['account.move.line'].search([('move_id','=',linea[12])])
            if busines:
                for y in busines:
                    if y.product_id.as_bussiness_id:
                        diario+=y.product_id.as_bussiness_id.name + ', '
                words = diario
                words=words.lower()
                no_repetidos=words.split()
                no_repetidos=" ".join(sorted(set(no_repetidos), key=no_repetidos.index))
                
            descuento=0.0          
            lineas_factura = self.env['account.move.line'].search([('move_id','=',linea[12])])
            if lineas_factura:
                for j in lineas_factura:
                    if j.discount:
                        descuento+=(j.price_unit*(j.discount/100))*j.quantity
            sheet.write(filas, 2, no_repetidos, number_left) #negocio
            sheet.write(filas, 3, linea[2], number_right)   #nit cliente
            sheet.write(filas, 4, linea[3], number_right)   #razon social
            sheet.write(filas, 5, linea[4], number_right) #autorizacion
            sheet.write(filas, 6, linea[5], number_right) #cod control
            sheet.write(filas, 7, linea[6], number_right) #importe
            sheet.write(filas, 8, descuento, number_right) #descuento
            sheet.write(filas, 9, linea[7], number_right) #importe neto facrura
            sheet.write(filas, 10, linea[13], number_right) #nro factrura
            sheet.write(filas, 11, linea[9], number_right) #fecha factura
            sheet.write(filas, 12, linea[10], number_left) #vendedor
            sheet.write(filas, 13, linea[11], number_left) #forma de pago
            filas+=1
                
            if linea[6] == None:
                total_omporte_bruto+=0
            else:
                total_omporte_bruto+=linea[6]
                
            if descuento == None:
                total_descuento+=0
            else:
                total_descuento+=descuento
                
            if linea[7] == None:
                total_improte_neto_Facura+=0
            else:
                total_improte_neto_Facura+=linea[7]
        sheet.merge_range('A'+str(filas+1)+':G'+str(filas+1)+'', 'TOTALES', totales_Azul)
        sheet.write(filas, 7, total_omporte_bruto, totales_Azul) 
        sheet.write(filas, 8, total_descuento, totales_Azul) 
        sheet.write(filas, 9, total_improte_neto_Facura, totales_Azul) 
        sheet.write(filas, 10, '', totales_Azul) 
        sheet.write(filas, 11, '', totales_Azul) 
        sheet.write(filas, 12, '', totales_Azul) 
        sheet.write(filas, 13, '', totales_Azul) 
        
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
    
    def nombre_asesor(self,data):
        dict_aux = []
        almacen=data['asesor']
        if almacen:
            for line in almacen:
                dict_aux.append(line)
        filtro_almacenes_name = 'Varios'
        for y in dict_aux:
            almacen_obj = self.env['res.users'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['res.users'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name
        