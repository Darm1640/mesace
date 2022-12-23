import datetime
from re import I
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

class as_pago_futuro_xlsx(models.AbstractModel):
    _name = 'report.as_bo_hr.as_pago_futuro.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('HOJA DE PAGOS FUTURO')
        #estilos
        titulo1 = workbook.add_format({'font_size':20,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4','top': True, 'bottom': True, })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3_dere = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })
        
        titulo5 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo9 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo6 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo12 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo7 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
        titulo8 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00'})
        number_dias =  workbook.add_format({'font_size': 9, 'align': 'center', 'num_format': '#,##0'})

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
        sheet.set_column('P:P',25, letter1)
        sheet.set_column('Q:Q',25, letter1)
        sheet.set_column('R:R',25, letter1)
        sheet.set_column('S:S',25, letter1)
        sheet.set_column('T:T',18, letter1)
        sheet.set_column('U:U',18, letter1)
        sheet.set_column('V:V',18, letter1)
        sheet.set_column('W:W',25, letter1)
        # Titulos, subtitulos, filtros y campos del reporte  
        sheet.merge_range('A4:W4', 'PLANILLA DE PAGO FUTURO', titulo1)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})   
        filastitle=4
        sheet.write(0, 20, 'NIT: ', titulo3) 
        sheet.write(1, 20, 'DIRECCION: ', titulo3) 
        sheet.write(2, 20, 'CELULAR, TELEFONO:', titulo3) 
        sheet.merge_range('V1:W1', str(self.env.user.company_id.vat), titulo3_dere)
        sheet.merge_range('V2:W2', str(self.env.user.company_id.street), titulo3_dere)
        sheet.merge_range('V3:W3', str(self.env.user.company_id.phone), titulo3_dere)   
        sheet.write(filastitle, 0, 'No', tituloAzul)  
        sheet.write(filastitle, 1, '(13) TIPO', tituloAzul)
        sheet.write(filastitle, 2, '(14) No', tituloAzul)
        sheet.write(filastitle, 3, '(14) EXTENSIÓN', tituloAzul)   
        sheet.write(filastitle, 4, '(15) NUA/CUA', tituloAzul)   
        sheet.write(filastitle, 5, '(A) 1er. APELLIDO (PATERNO)', tituloAzul) 
        sheet.write(filastitle, 6, '(B) 2do. APELLIDO (MATERNO)', tituloAzul)
        sheet.write(filastitle, 7, '(C) APELLIDO CASADA', tituloAzul)
        sheet.write(filastitle, 8, '(D)  PRIMER NOMBRE', tituloAzul)
        sheet.write(filastitle, 9, '(E) SEGUNDO NOMBRE', tituloAzul)
        sheet.write(filastitle, 10,'(F) DEPARTAMENTO', tituloAzul)   
        sheet.write(filastitle, 11, '(17) NOVEDAD I/R/L/S', tituloAzul)   
        sheet.write(filastitle, 12, '(18) FECHA NOVEDAD dd/mm/aaaa', tituloAzul) 
        sheet.write(filastitle, 13, '(19) DIAS COTIZADOS', tituloAzul)
        sheet.write(filastitle, 14, '(20) TIPO DE ASEGURADO (M/C/E)', tituloAzul)
        sheet.write(filastitle, 15, '(21)  TOTAL GANADO DEPENDIENTE < 65 AÑOS O ASEGURADO CON PENSION DEL SIP < 65 AÑOS QUE DECIDE APORTAR AL SIP', tituloAzul)     
        sheet.write(filastitle, 16, '(22) TOTAL GANADO DEPENDIENTE > 65 AÑOS O ASEGURADO CON PENSION DEL SIP > 65 AÑOS QUE DECIDE APORTAR AL SIP', tituloAzul)    
        sheet.write(filastitle, 17, '(23) TOTAL GANADO ASEGURADO CON PENSION DEL SIP < 65 AÑOS QUE DECIDE NO APORTAR AL SIP', tituloAzul)
        sheet.write(filastitle, 18, '(24)  TOTAL GANADO ASEGURADO CON PENSION AL SIP > 65 AÑOS QUE DECIDE NO APORTAR AL SIP', tituloAzul)
        sheet.write(filastitle, 19, '(25) COTIZACION ADICIONAL', tituloAzul)
        sheet.write(filastitle, 20, '(26) TOTAL GANADO FONDO DE VIVIENDA', tituloAzul)
        sheet.write(filastitle, 21, '(27) TOTAL GANADO FONDO SOLIDARIO', tituloAzul)
        sheet.write(filastitle, 22, '(28) TOTAL GANADO FONDO SOLIDARIO MINERO', tituloAzul)
        
        
        
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['as_payslip_run_id'])])
        filastitle+=1
        monto_sueldos = 0.0
        contador = 0
        for linea in payslip.slip_ids:
            if linea.employee_id.as_name_afp.name == 'Futuro':
                sheet.write(filastitle, 0, contador, titulo5)
                contador+=1
                if linea.employee_id.as_documento != False:
                    sheet.write(filastitle, 1, linea.employee_id.as_documento, number_center)
                if linea.employee_id.identification_id != False:    
                    sheet.write(filastitle, 2, linea.employee_id.identification_id, number_right)
                if linea.employee_id.as_expedito != False: 
                    sheet.write(filastitle, 3, linea.employee_id.as_expedito, number_dias)
                if linea.employee_id.as_nua != False:
                    sheet.write(filastitle, 4, linea.employee_id.as_nua, number_right)
                if linea.employee_id.apellido_1 != False: 
                    sheet.write(filastitle, 5, linea.employee_id.apellido_1, number_left)
                if linea.employee_id.apellido_2 != False: 
                    sheet.write(filastitle, 6, linea.employee_id.apellido_2, number_left)
                if linea.employee_id.apellido_3 != False: 
                    sheet.write(filastitle, 7, linea.employee_id.apellido_3, number_left)
                if linea.employee_id.nombre != False: 
                    sheet.write(filastitle, 8, linea.employee_id.nombre, number_left)
                if linea.employee_id.nombre_2 != False: 
                    sheet.write(filastitle, 9, linea.employee_id.nombre_2, number_left)
                if linea.employee_id.as_lugar_de_trabajo.name != False: 
                    sheet.write(filastitle, 10, linea.employee_id.as_lugar_de_trabajo.name, number_left)    
                
                if linea.contract_id.date_start >= linea.date_from and linea.contract_id.date_start <= linea.date_to:
                    sheet.write(filastitle, 11, 'I', titulo5)
                    sheet.write(filastitle, 12, linea.contract_id.date_start.strftime('%d/%m/%Y'), titulo5)
                elif linea.contract_id.date_end and linea.contract_id.date_end <= linea.date_to and linea.contract_id.date_end >= linea.date_from:
                    sheet.write(filastitle, 11, 'R', titulo5)
                    sheet.write(filastitle, 12, linea.contract_id.date_end.strftime('%d/%m/%Y'), titulo5)
                    
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
                    sheet.write(filastitle, 13,dias_trabajados, number_dias) #dias
                if linea.employee_id.as_tipo_asegurado != False:
                    sheet.write(filastitle, 14, linea.employee_id.as_tipo_asegurado, number_dias) #tipo_asegurado
                sheet.write(filastitle, 15, self.get_total_rules(linea.id,'SUBT',linea.employee_id.id,linea.contract_id.id), number_right)
                monto_sueldos +=  self.get_total_rules(linea.id,'SUBT',linea.employee_id.id,linea.contract_id.id)
                sheet.write(filastitle, 16, 0, number_right)
                sheet.write(filastitle, 17, 0, number_right)
                sheet.write(filastitle, 18, 0, number_right)
                sheet.write(filastitle, 19, 0, number_right)
                sheet.write(filastitle, 20, self.get_total_rules(linea.id,'SUBT',linea.employee_id.id,linea.contract_id.id), number_right)
                sheet.write(filastitle, 21, self.get_total_rules(linea.id,'SUBT',linea.employee_id.id,linea.contract_id.id), number_right)
                sheet.write(filastitle, 22, 0, number_right)
                filastitle+=1
        sheet.write(filastitle, 15, monto_sueldos, number_right_bold) 
        sheet.write(filastitle, 20, monto_sueldos, number_right_bold)
        sheet.write(filastitle, 21, monto_sueldos, number_right_bold)
            
    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0 
        

