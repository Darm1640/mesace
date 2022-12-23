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
    _name = 'report.as_cl_account_treasury.as_report_checks.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Reporte de Cheques')
        #estilos
        titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
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

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00'})
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

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',18, letter1)
        sheet.set_column('B:B',18, letter1)
        sheet.set_column('C:C',20, letter1)
        sheet.set_column('D:D',22, letter1)
        sheet.set_column('E:E',18, letter1)
        sheet.set_column('F:F',19, letter1)
        sheet.set_column('G:G',15, letter1)
        sheet.set_column('H:H',10, letter1)
        sheet.set_column('I:I',10, letter1)
        sheet.set_column('J:J',10, letter1)
        sheet.set_column('K:K',10, letter1)
        sheet.set_column('L:L',12, letter1)
        sheet.set_column('M:M',12, letter1)

        #defincion de filtros para reportes
 
     
        fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')

        # Titulos, subtitulos, filtros y campos del reporte  
        sheet.merge_range('A4:F4', 'REPORTES DE CHEQUES', titulo1)
        sheet.merge_range('A5:F5', fecha_inicial +' - '+ fecha_final, titulo2)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})     
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        filastitle=9
        sheet.write(0, 4, 'NIT: ', titulo3) 
        sheet.write(1, 4, 'DIRECCION: ', titulo3) 
        sheet.write(2, 4, 'CELULAR, TELEFONO:', titulo3)   
        sheet.write(7, 4, 'Fecha de impresion: ', titulo4)
        sheet.write(7, 5, fecha_actual, titulo3) 
        sheet.write(6, 0, 'Usuario:', titulo4)
        sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(7, 0, '', titulo4)
        sheet.write(7, 1, '', titulo3)
        sheet.write(filastitle, 0, 'Nro', tituloAzul)  
        sheet.write(filastitle, 1, 'Fecha Vencimiento', tituloAzul)
        sheet.write(filastitle, 2, 'Nro Cheque', tituloAzul)
        sheet.write(filastitle, 3, 'Secuencia', tituloAzul)   
        sheet.write(filastitle, 4, 'Moneda', tituloAzul)   
        sheet.write(filastitle, 5, 'Monto', tituloAzul) 
        filas= 10
        consulta_product= ("""
            SELECT 
            (ch.as_date_expire AT TIME ZONE 'UTC' AT TIME ZONE 'BOT'),
            ch.as_num_ckeck, 
            ch.name, 
            rc.name, 
            ch.as_amount
            
            FROM as_check_control ch
            join res_currency rc on rc.id = ch.as_currency_id
            where
            (ch.as_date_expire AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+ """'
            AND (ch.as_date_expire AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+ """' 
            and state = 'draft'
            ORDER BY ch.as_date_expire asc
            """)

        self.env.cr.execute(consulta_product)
        cheques = [j for j in self.env.cr.fetchall()]
        cont=0
        total = 0.0
        for linea in cheques:
            cont+=1
            sheet.write(filas, 0, cont, letter4G)  
            sheet.write(filas, 1, linea[0].strftime('%d/%m/%Y'), letter4G)
            sheet.write(filas, 2, linea[1], letter4G)
            sheet.write(filas, 3, linea[2], letter4G)   
            sheet.write(filas, 4, linea[3], letter4G)   
            sheet.write(filas, 5, linea[4], letter4B) 
            filas+=1
            total+=linea[4]
        sheet.merge_range('A'+str(filas+1)+':E'+str(filas+1)+'', 'Total', tituloAzul_D)
        sheet.write(filas, 5, total, tituloAzul_D) 
            
        
    
                