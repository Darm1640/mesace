# -*- coding: utf-8 -*-
import calendar
import xlsxwriter
import pytz
from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from datetime import datetime, timedelta, date
from time import mktime
from datetime import date, datetime
import time
from datetime import datetime, timedelta
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
class as_facturas_pagadas_pendientes(models.AbstractModel):
    _name = 'report.as_spectrocom_sales.reporte_facturas_paga_pendi.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('FACTURAS PAGADAS Y PENDIENTES')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'text_wrap': True,})
        number_subtitulos=workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True })
        totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  'bold':True })
        totales_valores = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  })
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True,})
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#A9A9A9'})

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
        sheet.set_column('A:A',20, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',15, letter1)
        sheet.set_column('D:D',15, letter1)
        sheet.set_column('E:E',35, letter1)
        sheet.set_column('F:F',35, letter1)
        sheet.set_column('G:G',15, letter1)
        sheet.set_column('H:H',15, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:H5', 'REPORTE FACTURADO Y PENDIENTE DE FACTURAR', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.38, 'y_scale': 0.17})
        sheet.write(7, 0, 'Usuario', titulo4)
        sheet.write(7, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(8, 0, 'Fecha de impresion: ', titulo4)
        sheet.write(8,1, fecha, titulo3)
        sheet.merge_range('A6:H6', fecha_inicial +' - '+ fecha_final, titulo1)
        sheet.write(0, 5, 'NIT: ', titulo3) 
        sheet.write(1, 5, 'DIRECCION: ', titulo3) 
        sheet.write(2, 5, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('G1:H1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('G2:H2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('G3:H3', str(self.env.user.company_id.phone), titulo3derecha) 
        
        sheet.write(10, 0, 'TIPO', titulo2) 
        sheet.write(10, 1, 'N°', titulo2) 
        sheet.write(10, 2, 'FECHA', titulo2) 
        sheet.write(10, 3, 'CC', titulo2)
        sheet.write(10, 4, 'NOMBRE CLIENTE', titulo2)
        sheet.write(10, 5, 'REFERENCIA', titulo2)
        sheet.write(10, 6, 'IMPORTE ', titulo2)
        sheet.write(10, 7, 'FACTURADO ', titulo2)
        filas = 11
        # Preparando variables para cada casod e consulta
        dict_clientes = []
        if data['form']['as_cliente']:
            for ids in data['form']['as_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND rp.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''

        consulta_product= ("""
            select 
                    am.name as "nombre factura",
                    am.name as "codigo_correlativo",
                     to_char((( am.invoice_date AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) AS "fecha_factura",
                    am.as_complemento_nit as "cc",
                    rp.name as "cliente",
                    atp.name as "nombre_proyecto",
                    so.amount_total as "venta_total",
                    am.amount_total as "factura_total",
                    am.currency_id as "tipo_moneda",
                    so.currency_id as "tipo_moneda_venta"
                    from account_move as am
                    left join res_partner as rp on rp.id=am.partner_id
                    left join sale_order as so on so.name = am.invoice_origin
                    left join as_template_project as atp on atp.id = so.as_template_id
            where
            am.state='posted' AND
            am.move_type='out_invoice' AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+ """' AND
            (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+ """'
            """+str(filtro_clientes)+"""
            ORDER BY am.invoice_date desc
            """)

        self.env.cr.execute(consulta_product)
        querys = [j for j in self.env.cr.fetchall()]
        cont=0
        for linea in querys:            
            sheet.write(filas, 0, linea[0], number_right) #nombre_factura 
            sheet.write(filas, 1, linea[1][2:], number_right) #nombre_factura prefijo
            sheet.write(filas, 2, linea[2], number_right) #fecha_factura
            sheet.write(filas, 3, linea[3], number_right)   #CC
            sheet.write(filas, 4, linea[4], number_left)   #Cliente
            sheet.write(filas, 5, linea[5], number_left)   #nombre_proyecto
            if linea[9] != 62 and linea[9] != None:
                if linea[6] != None:
                    sheet.write(filas, 6, str(linea[6]) +' '+ 'Sus', number_right) #venta_total
                else:
                    sheet.write(filas, 6, '0' +' '+ 'Sus', number_right) #venta_total
            else:
                if linea[6] != None:
                    sheet.write(filas, 6, str(linea[6]) +' '+ 'Bs.', number_right) #venta_total
                else:
                    sheet.write(filas, 6, '0' +' '+ 'Bs.', number_right) #venta_total
                
            if linea[8] != 62 and linea[8] != None:
                if linea[7] != None:
                    sheet.write(filas, 7, str(linea[7]) +' '+ 'Sus', number_right) #FACTURA_TOTAL
                else:
                    sheet.write(filas, 7, '0' +' '+ 'Sus', number_right) #FACTURA_TOTAL
            else:
                if linea[7] != None:
                    sheet.write(filas, 7, str(linea[7]) +' '+ 'Bs.', number_right) #FACTURA_TOTAL
                else:
                    sheet.write(filas, 7, '0' +' '+ 'Bs.', number_right) #FACTURA_TOTAL
            filas+=1
    
    def cortar_prefijos(inp):
        return hex(int(inp)).lstrip("0x").upper().rstrip("L")