import datetime
import xlsxwriter
from openpyxl.styles import Alignment
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

class as_pago_prevision_xlsx(models.AbstractModel):
    _name = 'report.as_bo_hr.as_pago_prevision.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('HOJA DE PAGOS Y PREVISION')
        #estilos
        titulo1 = workbook.add_format({'font_size':20,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4','top': True, 'bottom': True, })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
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
        number_right_dias = workbook.add_format({'font_size': 9, 'align': 'center', 'num_format': '#,##0'})
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
        letter4S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter41S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
        letter41Sr = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True,'color': 'red'})
        tituloAzul.set_align('vcenter')
        letter_locked = letter3
        letter_locked.set_locked(False)

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',18, letter1)
        sheet.set_column('B:B',18, letter1)
        sheet.set_column('C:C',18, letter1)
        sheet.set_column('D:D',18, letter1)
        sheet.set_column('E:E',18, letter1)
        sheet.set_column('F:F',18, letter1)
        sheet.set_column('G:G',18, letter1)
        sheet.set_column('H:H',18, letter1)
        sheet.set_column('I:I',18, letter1)
        sheet.set_column('J:J',18, letter1)
        sheet.set_column('K:K',18, letter1)
        sheet.set_column('L:L',18, letter1)
        sheet.set_column('M:M',18, letter1)
        sheet.set_column('N:N',18, letter1)
        sheet.set_column('O:O',18, letter1)
        # Titulos, subtitulos, filtros y campos del reporte  
        # sheet.merge_range('A4:O4', 'PLANILLA DE PAGOS PREVISION', titulo1)
        # url = image_data_uri(self.env.user.company_id.logo)
        # image_data = BytesIO(urlopen(url).read())
        # sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})   
        filastitle=0
        # sheet.write(0, 13, 'NIT: ', titulo3) 
        # sheet.write(1, 13, 'DIRECCION: ', titulo3) 
        # sheet.write(2, 13, 'CELULAR, TELEFONO:', titulo3)
        sheet.write(filastitle, 0, 'TIPO DOC.', tituloAzul)  
        sheet.write(filastitle, 1, 'NUMERO DOCUMENTO', tituloAzul)
        sheet.write(filastitle, 2, 'ALFANUMERICO DEL DOCUMENTO', tituloAzul)
        sheet.write(filastitle, 3, 'NUA / CUA', tituloAzul)   
        sheet.write(filastitle, 4, 'AP. PATERNO', tituloAzul)   
        sheet.write(filastitle, 5, 'AP. MATERNO', tituloAzul) 
        sheet.write(filastitle, 6, 'AP. CASADA', tituloAzul)
        sheet.write(filastitle, 7, 'PRIMER NOMBRE', tituloAzul)
        sheet.write(filastitle, 8, 'SEG. NOMBRE', tituloAzul)
        sheet.write(filastitle, 9, 'NOVEDAD', tituloAzul)
        sheet.write(filastitle, 10, 'FECHA NOVEDAD', tituloAzul)   
        sheet.write(filastitle, 11, 'DIAS', tituloAzul)   
        sheet.write(filastitle, 12, 'TOTAL GANADO', tituloAzul) 
        sheet.write(filastitle, 13, 'TIPO COTIZANTE', tituloAzul)
        sheet.write(filastitle, 14, 'TIPO ASEGURADO', tituloAzul)
        
        # Preparando variables para cada casod e consulta

        # consulta_product= ("""
        #     SELECT 
        #     as_documento, identification_id, as_nua,
        #     apellido_1, apellido_2,apellido_3, nombre, 
        #     nombre_2, as_novedades, fecha_novedad, id,as_tipo_cotizante, as_tipo_asegurado
        #     FROM hr_employee
        #     """)
        # self.env.cr.execute(consulta_product)
        # querys = [j for j in self.env.cr.fetchall()]
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['as_payslip_run_id'])])
        filastitle+=1
        monto_sueldos = 0.0
        for linea in payslip.slip_ids:
            if linea.employee_id.as_name_afp.name == 'Prevision':
                if linea.employee_id.as_documento != False:
                    sheet.write(filastitle, 0, linea.employee_id.as_documento, titulo5)
                if linea.employee_id.identification_id != False:    
                    sheet.write(filastitle, 1, linea.employee_id.identification_id, titulo5)
                if linea.employee_id.identification_id != False and linea.employee_id.as_complemento_ci != False:
                    sheet.write(filastitle, 2, str(linea.employee_id.identification_id) +' '+ str(linea.employee_id.as_complemento_ci), titulo5)
                if linea.employee_id.as_nua != False:
                    sheet.write(filastitle, 3, linea.employee_id.as_nua, titulo5)
                if linea.employee_id.apellido_1 != False: 
                    sheet.write(filastitle, 4, linea.employee_id.apellido_1, titulo5)
                if linea.employee_id.apellido_2 != False: 
                    sheet.write(filastitle, 5, linea.employee_id.apellido_2, titulo5)
                if linea.employee_id.apellido_3 != False: 
                    sheet.write(filastitle, 6, linea.employee_id.apellido_3, titulo5)
                if linea.employee_id.nombre != False: 
                    sheet.write(filastitle, 7, linea.employee_id.nombre, titulo5)
                if linea.employee_id.nombre_2 != False: 
                    sheet.write(filastitle, 8, linea.employee_id.nombre_2, titulo5)
                
                if linea.contract_id.date_start >= linea.date_from and linea.contract_id.date_start <= linea.date_to:
                    sheet.write(filastitle, 9, 'I', titulo5)
                    sheet.write(filastitle, 10, linea.contract_id.date_start.strftime('%d/%m/%Y'), titulo5)
                elif linea.contract_id.date_end and linea.contract_id.date_end <= linea.date_to and linea.contract_id.date_end >= linea.date_from:
                    sheet.write(filastitle, 9, 'R', titulo5)
                    sheet.write(filastitle, 10, linea.contract_id.date_end.strftime('%d/%m/%Y'), titulo5)
                
                
                consulta_product= ("""
                SELECT 
                id
                FROM hr_employee
                """)
                self.env.cr.execute(consulta_product)
                querys = [j for j in self.env.cr.fetchall()]
                for dias_worked in linea:
                    dias_trabajados=0
                    for dias_working in dias_worked.worked_days_line_ids:
                        if dias_working.name == 'Attendance':
                            dias_trabajados+=dias_working.number_of_days
                    sheet.write(filastitle, 11,dias_trabajados, number_right_dias) #dias
                sheet.write(filastitle, 12, self.get_total_rules(linea.id,'SUBT',linea.employee_id.id,linea.contract_id.id), number_right)
                monto_sueldos +=  self.get_total_rules(linea.id,'SUBT',linea.employee_id.id,linea.contract_id.id)
                # if linea.employee_id.as_tipo_cotizante != False:
                #     sheet.write(filastitle, 13, linea.employee_id.as_tipo_cotizante, number_right_dias) #tipo_cotizante
                sheet.write(filastitle, 13, 1, number_right_dias) #tipo_cotizante
                if linea.employee_id.as_tipo_asegurado != False:
                    sheet.write(filastitle, 14, linea.employee_id.as_tipo_asegurado, number_right_dias) #tipo_asegurado
                filastitle+=1
        sheet.write(filastitle, 12, monto_sueldos, number_right_bold) 
            # sheet.write(filas, 0, linea[0], number_center) #as_documento 
            # sheet.write(filas, 1, linea[1], number_right) #identification_id
            # sheet.write(filas, 2, '', number_right) #alfanumerico
            # sheet.write(filas, 3, linea[2], number_left) #as_nua
            # sheet.write(filas, 4, linea[3], number_left) #apellido_1
            # sheet.write(filas, 5, linea[4], number_left) #apellido_2
            # sheet.write(filas, 6, linea[5], number_left) #apellido_3
            # sheet.write(filas, 7, linea[6], number_left) #nombre
            # sheet.write(filas, 8, linea[7], number_left) #nombre_2
            # sheet.write(filas, 9, linea[8], number_center) #as_novedades
            # if linea[9]:
            #     sheet.write(filas, 10, str(linea[9].year) + str(linea[9].month) +str(linea[9].day), number_right) #fecha_novedad
            # if linea[10]:
            #     dias=self.env['hr.payslip'].search([('employee_id','=',linea[10])],limit=1)
            #     if dias:
            #         dias_trabajados=dias.worked_days_line_ids.number_of_days
            #         sheet.write(filas, 11,dias_trabajados, number_right) #dias
            # sheet.write(filas, 13, linea[11], number_right) #tipo_cotizante
            # sheet.write(filas, 14, linea[12], number_left) #tipo_asegurado
            # filas+=1
            
    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0 
        

