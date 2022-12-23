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

class as_excel_quincena(models.AbstractModel):
    _name = 'report.as_bo_hr_bonus_discount.as_pdf_report_excel.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Reporte de Quincena')
        #estilos
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,})

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_total = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True,  'bottom': True, 'top': True,'left': True, 'right': True,'bold':True})
        number_total_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,'bold':True})
        number_total_right_co_uno = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_right_col = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 9, 'align': 'center','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True,'font_size': 11,'font_name': 'Lucida Sans',})
       
        letter_locked = letter3
        letter_locked.set_locked(False)
        number_left.set_align('vcenter')
        number_total_right_co_uno.set_align('vcenter')
        number_total.set_align('vcenter')
        number_total_right.set_align('vcenter')
        number_center.set_align('vcenter')
        tituloAzul.set_align('vcenter')
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',14, letter1)
        sheet.set_column('B:B',20, letter1)
        sheet.set_column('C:C',14, letter1)
        sheet.set_column('D:D',14, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',18, letter1)
        sheet.set_column('G:G',14, letter1)
        sheet.set_column('H:H',20, letter1)
        sheet.set_column('I:I',14, letter1)
        sheet.set_column('J:J',14, letter1)
        
        filastitle=0
        sheet.write(filastitle, 0, 'Convenio', tituloAzul)  
        sheet.write(filastitle, 1, 'Cuenta Debito', tituloAzul)
        sheet.write(filastitle, 2, 'Producto', tituloAzul)
        sheet.write(filastitle, 3, 'Moneda Pago', tituloAzul)   
        sheet.write(filastitle, 4, 'Identificador Planilla', tituloAzul)   
        sheet.write(filastitle, 5, 'Fecha Aplicacion', tituloAzul) 
        sheet.write(filastitle, 6, 'Fecha Vencimiento', tituloAzul) 
        sheet.write(filastitle, 7, 'Total Abonar', tituloAzul) 
        sheet.write(filastitle, 8, 'Tipo Pago Planilla', tituloAzul) 
        sheet.write(filastitle, 9, 'Nro. Registros', tituloAzul) 
        
        filas= 1
                
        sheet.write(filas, 0, 849, number_center)
        sheet.write(filas, 1, 262610, number_center)
        sheet.write(filas, 2, 100, number_center)
        sheet.write(filas, 3, 1, number_center)
        sheet.write(filas, 4, lines.name, number_left)
        sheet.write(filas, 5, lines.as_date_start.strftime('%d/%m/%Y'), number_total_right)
        sheet.write(filas, 6, '', number_total_right)
        sheet.write(filas, 7, '', number_total_right)
        sheet.write(filas, 8, 1, number_center)
        
        sheet.write(filas+1, 0, 'CI', tituloAzul)  
        sheet.write(filas+1, 1, 'Nombre Beneficiario', tituloAzul)
        sheet.write(filas+1, 2, 'Cuenta de Abono', tituloAzul)
        sheet.write(filas+1, 3, 'producto', tituloAzul)   
        sheet.write(filas+1, 4, 'Fecha Aplicacion', tituloAzul) 
        sheet.write(filas+1, 5, 'Forma de Pago', tituloAzul) 
        sheet.write(filas+1, 6, 'Monto', tituloAzul) 
        sheet.write(filas+1, 7, 'Referencia', tituloAzul) 
        sheet.write(filas+1, 8, 'Correo', tituloAzul)
        
        contenido_lineas = self.env['as.bonus.discount.line'].sudo().search([('id', '=', lines.id)])
        lines.as_summary_ids
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y')
        
        fila_caja = 3
        contador = 0
        abono_total = 0.0
        if lines.as_summary_ids:
            for linea_caja in lines.as_summary_ids:
                if linea_caja.as_employee_id.identification_id:
                    sheet.write(fila_caja, 0, linea_caja.as_employee_id.identification_id, number_right)
                else:
                    sheet.write(fila_caja, 0, '', number_right)
                if linea_caja.as_employee_id.name:
                    sheet.write(fila_caja, 1, linea_caja.as_employee_id.name, number_left)
                else:
                    sheet.write(fila_caja, 1, '', number_left)
                if linea_caja.as_employee_id.bank_account_id.acc_number:
                    sheet.write(fila_caja, 2, linea_caja.as_employee_id.bank_account_id.acc_number, number_right)
                else:
                    sheet.write(fila_caja, 2, '', number_right)
                sheet.write(fila_caja, 3, 200, number_center)
                sheet.write(fila_caja, 4, fecha, number_right)
                sheet.write(fila_caja, 5, 1, number_center)
                if linea_caja.as_bonus_amount:
                    sheet.write(fila_caja, 6, linea_caja.as_bonus_amount, number_right)
                    abono_total+=linea_caja.as_bonus_amount
                else:
                    sheet.write(fila_caja, 6, '', number_right)
                if lines.name:
                    sheet.write(fila_caja, 7, lines.name, number_left)
                else:
                    sheet.write(fila_caja, 7, '', number_left)
                sheet.write(fila_caja, 8, '', number_left)
                contador+=1
                fila_caja+=1
                
        sheet.write(1, 9, contador, tituloAzul)  
        sheet.write(1, 7, abono_total, tituloAzul)      
                
        
    
                