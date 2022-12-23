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

class as_resumen_cuentas(models.AbstractModel):
    _name = 'report.as_bo_accounting.as_resumen_cuentas_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Resumen de estado de cuentas detallado')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo1_debajo = workbook.add_format({'font_size': 15, 'align': 'center', 'text_wrap': True,'top': False, 'bold':True, 'bottom': True })

        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', })
        number_left_totales = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00','bg_color':'#A9A9A9' })
        number_right_totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color':'#A9A9A9' })

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
        sheet.set_column('A:A',15, letter1)
        sheet.set_column('B:B',28, letter1)
        sheet.set_column('C:C',15, letter1)
        sheet.set_column('D:D',20, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)

        
        sheet.merge_range('A12:D12', 'PROVEEDORES', titulo2)
        sheet.write(11, 4, 'IMPORTE', titulo2) 
        sheet.write(11, 5, 'SALDO', titulo2) 
        # sheet.write(11, 3, 'DEBE', titulo2)
        # sheet.write(11, 4, 'HABER', titulo2)
        # sheet.write(11, 5, 'SALDO', titulo2)
        
        # fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        # fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        dict_product=[] #aqui se guardan los ids del wizard
        filtro_products_po =''
        filtro_products_po =''
        if data['form']['as_nombre_cliente']:
            for line in data['form']['as_nombre_cliente']:
                dict_product.append(line)
        if dict_product: 
            whe = 'AND aml.partner_id IN'
            filtro_products_po += whe
            filtro_products_po +=str(dict_product).replace('[','(').replace(']',')')
        else:
            filtro_products_po += ''
        
        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:F5', 'ESTADO DE CUENTA', titulo1)
        sheet.merge_range('A6:F6', '(Expresado en bolivianos)', titulo1_debajo)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        # fecha_inicial = datetime.strptime(str(data['form']['fecha_inicial']), '%Y').strftime('%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:B5', url, {'image_data': image_data,'x_scale': 0.28, 'y_scale': 0.17})
        # sheet.write(7, 0, 'Tipo de Producto', titulo4)
        # sheet.merge_range('B8:C8', self.tipo_producto(data['form']), titulo3)
        sheet.write(8, 0, 'Usuario: ', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(9, 0, 'CUENTA: ', titulo4)
        sheet.write(9, 1, self.nombre_cuentas(data['form']),titulo3)
        # sheet.write(7, 10, 'Clientes: ', titulo4)
        # sheet.merge_range('L8:M8', self.nombre_cliente(data['form']), titulo3)
        # sheet.write(8, 10, 'Divisa: ', titulo4)
        sheet.write(8, 3, 'Fecha de impresion: ', titulo4)
        sheet.write(8, 4, fecha, titulo3)
        # sheet.merge_range('A6:M6', ' GESTION['+ fecha_inicial +']', tituloAzul)
        sheet.write(0, 3, 'NIT: ', titulo3) 
        sheet.write(1, 3, 'DIRECCION: ', titulo3) 
        sheet.write(2, 3, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('E1:F1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('E2:F2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('E3:F3', str(self.env.user.company_id.phone), titulo3derecha) 
        filas= 12
        # Preparando variables para cada casod e consulta
        #consultas
        consulta_productos= ("""
                select 
                rp.name,
                sum(aml.debit) as debito,
                sum(aml.credit) as credito
                from account_move_line as aml
                left join account_account as aa on aa.id = aml.account_id
                left join res_partner as rp on rp.id = aml.partner_id
                left join account_move as am on am.id = aml.move_id
                
                where 
                am.state = 'posted'
                AND (am.as_contable is NULL OR am.as_contable = False)
                AND aml.account_id = '"""+str(data['form']['as_cuentas_proveedor'])+ """'
                """+str(filtro_products_po)+ """
                AND (aml.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+ """'
                AND (aml.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+ """'
                GROUP BY 1
                """)

        cont=0
        self.env.cr.execute(consulta_productos)
        productoslinea = [j for j in self.env.cr.fetchall()]
        cont_1 = 0.0
        cont_2 = 0.0
        if productoslinea != []:
            for linea in productoslinea:
                sheet.merge_range('A'+str(filas+1)+':D'+str(filas+1), linea[0], number_left)
                sheet.write(filas, 4, linea[1], number_right)
                cont_1+=linea[1]
                sheet.write(filas, 5, linea[1] - linea[2], number_right)
                cont_2+=linea[1] - linea[2]
                filas+=1
        sheet.merge_range('A'+str(filas+2)+':D'+str(filas+2), 'TOTAL ', number_left_totales)
        sheet.write(filas+1, 4, cont_1, number_right_totales)
        sheet.write(filas+1, 5, cont_2, number_right_totales)
        
    
    def nombre_cuentas(self,data):
        almacen=data['as_cuentas_proveedor']
        if almacen:
            filtro_nombre = self.env['account.account'].search([('id', '=', almacen)]).name
            filtro_code = self.env['account.account'].search([('id', '=', almacen)]).code
            nombre = str(filtro_code) + ' '+ str(filtro_nombre)
        return nombre
    
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