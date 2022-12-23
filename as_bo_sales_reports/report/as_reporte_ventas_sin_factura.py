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

class as_ventas_sin_Factura_report(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.as_ventas_sn_factura_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Resumen de Cuentas Cobrar')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'top': False, 'bold':True })
        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 10, 'align': 'left', 'num_format': '#,##0.00', 'text_wrap': True,'bottom': True, 'top': True, 'right': True, 'left': True, })
        letra_subvalores = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00','bg_color':'#F0FFFF','bold':True, 'bottom': True, 'top': True, 'right': True, 'left': True, })
        number_subtitulos=workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True })
        totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  'bold':True })
        totales_valores = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  })
        number_days=workbook.add_format({'font_size': 10, 'align': 'center','text_wrap': True,'bottom': True, 'top': True, 'right': True, 'left': True, })
        number_right = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True,'bottom': True, 'top': True, 'right': True, 'left': True, })
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'center', 'bold':True,'bg_color':'#A9A9A9','num_format': '#,##0.00', 'text_wrap': True,})

        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(True)
        totales_Azul = workbook.add_format({'font_size': 12, 'align': 'right', 'bold':True,'bg_color':'#F0F8FF'})
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        number_days.set_align('vcenter')
        number_left.set_align('vcenter')
        number_right.set_align('vcenter')
        sheet.set_column('A:N',10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',16, letter1)
        sheet.set_column('B:B',16, letter1)
        sheet.set_column('C:C',12, letter1)
        sheet.set_column('D:D',12, letter1)
        sheet.set_column('E:E',26, letter1)
        sheet.set_column('F:F',26, letter1)
        sheet.set_column('G:G',18, letter1)
        sheet.set_column('H:H',18, letter1)
        sheet.set_column('I:I',22, letter1)
        sheet.set_column('J:J',18, letter1)
        sheet.set_column('K:K',18, letter1)
        sheet.set_column('L:L',18, letter1)
        sheet.set_column('M:M',18, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:L5', 'REPORTE CONTROL DE SERVICIO Y VENTAS SIN FACTURA', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['fecha_inicial']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['fecha_final']), '%Y-%m-%d').strftime('%d/%m/%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.38, 'y_scale': 0.17})
        
        sheet.write(7, 0, 'Usuario', titulo4)
        sheet.write(7, 1, str(self.env.user.partner_id.name), titulo3)
    
        # sheet.write(8, 8, 'Clientes: ', titulo4)
        # sheet.merge_range('J9:L9', self.nombre_cliente(data['form']), titulo3)
        sheet.write(7, 9, 'Fecha de impresion: ', titulo4)
        sheet.write(7, 10, fecha, titulo3)
        sheet.merge_range('A6:L6', ' DE ['+ fecha_inicial +'] A [' + fecha_final + ']', tituloAzul)
        sheet.write(0, 9, 'NIT: ', titulo3) 
        sheet.write(1, 9, 'DIRECCION: ', titulo3) 
        sheet.write(2, 9, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('K1:L1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('K2:L2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('K3:L3', str(self.env.user.company_id.phone), titulo3derecha) 
        
        sheet.write(9, 0, 'CLIENTE', titulo2) 
        sheet.write(9, 1, 'NUMERO DE COTIZACION', titulo2) 
        sheet.write(9, 2, 'FECHA DE COTIZACION', titulo2) 
        sheet.write(9, 3, 'CANTIDAD', titulo2) 
        sheet.write(9, 4, 'PRODUCTO Y/O SERVICIO', titulo2) 
        sheet.write(9, 5, 'CATEGORIA DE PRODUCTO', titulo2)
        sheet.write(9, 6, 'ESTADO DE LA SUSCRIPCION', titulo2)
        sheet.write(9, 7, 'DIAS DE MORA ', titulo2)
        sheet.write(9, 8, 'TOTAL PEDIDO DE VENTA AUTORIZADO', titulo2)
        sheet.write(9, 9, 'MONTO PAGADO', titulo2)
        sheet.write(9, 10, 'SALDO DEUDOR', titulo2)
        sheet.write(9, 11, 'FECHA DE PAGO', titulo2)
        dict_clientes = []
        if data['form']['nombre_cliente']:
            for ids in data['form']['nombre_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND rp.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''
    
        filas=10
        #consuilta de fechas creditos
        consulta_cliente_servicio= ("""
        select 
        so.name,
        rp.name,
        arp.name,
        to_char(((so.date_order AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) as  "fecha",
        sol.product_uom_qty,
        pt.name,
        pc.name,
        so.amount_total, 
        so.as_pagado,
        so.as_saldo,
        so.id as "para entrar a la fecha del pago"
        from sale_order as so
        join res_partner as rp on rp.id = so.partner_id
        join as_template_project as arp on arp.id = so.as_template_id
        join sale_order_line as sol on sol.order_id = so.id
        join product_product as pp on pp.id = sol.product_id
        join product_template as pt on pt.id =pp.product_tmpl_id
        join product_category as pc on pc.id = pt.categ_id
        where  so.state = 'autotizada'
        AND (so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['fecha_inicial'])+ """' AND
        (so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['fecha_final'])+ """'
        """+str(filtro_clientes)+"""
        ORDER BY so.date_order desc
        """)
        # """+str(filtro_clientes)+"""
        self.env.cr.execute(consulta_cliente_servicio)
        querys_servicio = [j for j in self.env.cr.fetchall()] 

        for linea_servicio in querys_servicio:
            sheet.write(filas, 0, linea_servicio[1], number_left)
            sheet.write(filas, 1, linea_servicio[2], number_right)
            sheet.write(filas, 2, linea_servicio[3], number_right)
            sheet.write(filas, 3, linea_servicio[4], number_right)
            sheet.write(filas, 4, linea_servicio[5], number_left)
            sheet.write(filas, 5, linea_servicio[6], number_left)
            sheet.write(filas, 6, '', number_right)
            sheet.write(filas, 7, '', number_right)
            sheet.write(filas, 8, linea_servicio[7], number_right)
            sheet.write(filas, 9, linea_servicio[8], number_right)
            sheet.write(filas, 10, linea_servicio[9], number_right)
            pagos_so = self.env['account.move.line'].search([('sale_id', '=', linea_servicio[10])])
            fechas=''
            if pagos_so:
                for pagitos in pagos_so:
                    fechas += str(pagitos.date.strftime('%d/%m/%Y'))+' '
            sheet.write(filas, 11, fechas, number_right)
            filas +=1
        # sheet.merge_range('J'+str(filastitle+1)+':K'+str(filastitle+1), total_bob, color_cabecera_plomo)
        # sheet.write(filastitle, 11, total_usd, color_cabecera_plomo)
        
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

