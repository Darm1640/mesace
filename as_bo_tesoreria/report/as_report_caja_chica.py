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

class a_libro_historico_xlsx(models.AbstractModel):
    _name = 'report.as_bo_tesoreria.as_pdf_report_de_caja_chica.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Reporte de Cheques')
        #estilos
        titulo1 = workbook.add_format({'font_size': 20,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
        tituloAzul_D = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','num_format': '#,##0'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3_number = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
        titulo10 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
        titulo5 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo9 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo6 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo12 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo7 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
        titulo8 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_total = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True,  'bottom': True, 'top': True,'left': True, 'right': True,'bold':True})
        number_total_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,'bold':True})
        number_total_right_co_uno = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_datos = workbook.add_format({'font_size': 9, 'align': 'right','text_wrap': True,'bold':True})
        number_right_bold = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 9, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 9, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True,'font_size': 11,'font_name': 'Lucida Sans',})
        letter4 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter4C = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True,'color': '#000000','bg_color': '#F4F5F5','font_name': 'Lucida Sans', })
        letter4F = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True,'color': '#FFFFFF','bg_color': '#507AAA','font_name': 'Lucida Sans',})
        letter4G = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bold': True,'color': '#000000'})
        letter4B = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True, 'bold': True,'color': '#000000','num_format': '#,##0'})
        letter4S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter41S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
        letter41Sr = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True,'color': 'red'})
        letter_locked = letter3
        letter_locked.set_locked(False)
        number_left.set_align('vcenter')
        number_total_right_co_uno.set_align('vcenter')
        number_total.set_align('vcenter')
        number_total_right.set_align('vcenter')
        number_center.set_align('vcenter')
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',14, letter1)
        sheet.set_column('B:B',14, letter1)
        sheet.set_column('C:C',55, letter1)
        sheet.set_column('D:D',14, letter1)
        sheet.set_column('E:E',14, letter1)
        sheet.set_column('F:F',18, letter1)
        sheet.set_column('G:G',14, letter1)
        sheet.set_column('H:H',14, letter1)
        sheet.set_column('I:I',10, letter1)
        sheet.set_column('J:J',10, letter1)
        sheet.set_column('K:K',10, letter1)
        sheet.set_column('L:L',12, letter1)
        sheet.set_column('M:M',12, letter1)

        # Titulos, subtitulos, filtros y campos del reporte  
        sheet.merge_range('A4:F4', 'LIBRO DE CAJA', titulo1)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:C4', url, {'image_data': image_data,'x_scale': 0.19, 'y_scale': 0.13})     
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        filastitle=8
        sheet.write(0, 4, 'NIT: ', titulo3) 
        sheet.write(1, 4, 'DIRECCION: ', titulo3) 
        sheet.write(2, 4, 'CELULAR, TELEFONO:', titulo3)   
        sheet.write(6, 4, 'Fecha de impresion: ', titulo4)
        sheet.write(0, 5, self.env.user.company_id.vat, number_datos) 
        sheet.write(1, 5, self.env.user.company_id.street, number_datos) 
        sheet.write(2, 5, self.env.user.company_id.phone, number_datos) 
        sheet.write(6, 5, fecha_actual, titulo3) 
        sheet.write(5, 0, 'Caja:', titulo4)
        sheet.write(5, 1, lines.name, titulo3)
        sheet.write(6, 0, 'Usuario:', titulo4)
        sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
        # sheet.write(7, 0, '', titulo4)
        # sheet.write(7, 1, '', titulo3)
        sheet.write(filastitle, 0, 'FECHA', tituloAzul)  
        sheet.write(filastitle, 1, 'DOCUMENTO', tituloAzul)
        sheet.write(filastitle, 2, 'DESCRIPCION', tituloAzul)
        sheet.write(filastitle, 3, 'INGRESO', tituloAzul)   
        sheet.write(filastitle, 4, 'EGRESO', tituloAzul)   
        sheet.write(filastitle, 5, 'SALDO', tituloAzul) 
        filas= 9
        # linea_fecha = self.env['as.caja.chica'].sudo().search([('id', '=', invoice_id)])
        sheet.write(filas, 0, '', number_left)
        sheet.write(filas, 1, '', number_left)
        sheet.write(filas, 2, 'SALDO INICIAL CAJA', number_left)
        sheet.write(filas, 3, lines.as_saldo_inicial, number_total_right_co_uno) 
        sheet.write(filas, 5, lines.as_saldo_inicial, number_total_right_co_uno) 
        lineas_caja_chica = self.env['as.caja.chica'].sudo().search([('as_tesoreria_id', '=', lines.id)])
        fila_caja = 10
        fila_totales = fila_caja
        cont=0
        total=0
        valor = 0
        valorsito=0
        valores= 0
        vector_papa=0
        valor_total_egreso=0
        valor_total_saldo=0
        if lineas_caja_chica:
            for linea_caja in lineas_caja_chica:
                # reporte con sumas en caso de que se pida que el reporte sea con la s
                # restrriccion del estado cancelado
                if linea_caja.state == 'confirm': 
                    if cont == 0:
                        sheet.write(fila_caja, 0, str(linea_caja.date.day) + '/'+ str(linea_caja.date.month)+ '/'+str(linea_caja.date.year), number_total_right_co_uno)
                        sheet.write(fila_caja, 1, linea_caja.as_tipo_documento, number_left)
                        sheet.write(fila_caja, 2, linea_caja.as_nota, number_left)
                        sheet.write(fila_caja, 4, linea_caja.as_amount - linea_caja.as_descuento_tesoreria, number_total_right_co_uno)
                        valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                        vector_papa = lines.as_saldo_inicial - linea_caja.as_amount
                        sheet.write(fila_caja, 5, vector_papa, number_total_right_co_uno)
                    if cont == 1:
                        if linea_caja.state == 'confirm':
                            sheet.write(fila_caja+1, 0, str(linea_caja.date.day) + '/'+ str(linea_caja.date.month)+ '/'+str(linea_caja.date.year), number_total_right_co_uno)
                            sheet.write(fila_caja+1, 1, linea_caja.as_tipo_documento, number_left)
                            sheet.write(fila_caja+1, 2, linea_caja.as_nota, number_left)
                            sheet.write(fila_caja+1, 3, '', number_total_right_co_uno)
                            sheet.write(fila_caja+1, 4, linea_caja.as_amount - linea_caja.as_descuento_tesoreria, number_total_right_co_uno)
                            valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                            sheet.write(fila_caja+1, 5, vector_papa - linea_caja.as_amount, number_total_right_co_uno)
                            valorsito = vector_papa - linea_caja.as_amount
                            fila_caja+=1
                    if cont > 1:
                        if linea_caja.state == 'confirm':
                            sheet.write(fila_caja+1, 0, str(linea_caja.date.day) + '/'+ str(linea_caja.date.month)+ '/'+str(linea_caja.date.year), number_total_right_co_uno)
                            sheet.write(fila_caja+1, 1, linea_caja.as_tipo_documento, number_left)
                            sheet.write(fila_caja+1, 2, linea_caja.as_nota, number_left)
                            sheet.write(fila_caja+1, 3, '', number_total_right_co_uno)
                            sheet.write(fila_caja+1, 4, linea_caja.as_amount - linea_caja.as_descuento_tesoreria, number_total_right_co_uno)
                            valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                            sheet.write(fila_caja+1, 5, valorsito - linea_caja.as_amount , number_total_right_co_uno)
                            valorsito = valorsito - linea_caja.as_amount
                            fila_caja+=1
                            cont+=1
                    else:
                        cont+=1
        sheet.merge_range('A'+str(fila_caja+2)+':C'+str(fila_caja+2), 'TOTAL', number_total)
        sheet.write(fila_caja+1, 3,  lines.as_saldo_inicial  , number_total_right)
        sheet.write(fila_caja+1, 4, valor_total_egreso  , number_total_right)
        sheet.write(fila_caja+1, 5,  lines.as_saldo_inicial - valor_total_egreso , number_total_right)
        
    
                