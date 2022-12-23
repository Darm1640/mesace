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
    _name = 'report.as_bo_sale_route.as_cuadro_personal_retirado_xlsx.xlsx'
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
        sheet.set_column('B:B',35, letter1)
        sheet.set_column('C:C',35, letter1)
        sheet.set_column('D:D',20, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)

        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:B5', url, {'image_data': image_data,'x_scale': 0.28, 'y_scale': 0.17})

        sheet.merge_range('A5:F5', 'CUADRO DE PERSONAL RETIRADO', titulo1)
        sheet.write(6, 0, 'Usuario: ', titulo4)
        sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        sheet.write(6, 4, 'Fecha de impresion: ', titulo4)
        sheet.write(6, 5, fecha, titulo3)

        sheet.write(10, 0, 'DOCUMENTO DE IDENTIDAD', titulo2) 
        sheet.write(10, 1, 'NOMBRE Y APELLIDOS', titulo2) 
        sheet.write(10, 2, 'CARGO', titulo2) 
        sheet.write(10, 3, 'FECHA DE INGRESO', titulo2) 
        sheet.write(10, 4, 'FECHA DE RETIRO', titulo2) 
        sheet.write(10, 5, 'HABER BASICO', titulo2) 


        dict_empleado=[] #aqui se guardan los ids del wizard
        filtro_empleados_po =''
        filtro_empleados_po =''
        if data['form']['as_nombre_empleado']:
            for line in data['form']['as_nombre_empleado']:
                dict_empleado.append(line)
        if dict_empleado: 
            whe = 'AND hrc.employee_id IN'
            filtro_empleados_po += whe
            filtro_empleados_po +=str(dict_empleado).replace('[','(').replace(']',')')
        else:
            filtro_empleados_po += ''

        consulta_empleados= ("""
               select 
                hre.identification_id,
                hre.name, 
                hrj.name,
                hrc.date_start,
                hrc.date_end,
                hrc.as_monto
                from hr_contract as hrc
                left join hr_employee as hre on hre.id = hrc.employee_id
                left join hr_job as hrj on hrj.id = hrc.job_id

                where hrc.state = 'close'  """+str(filtro_empleados_po)+ """
                """)

        filas= 11
        self.env.cr.execute(consulta_empleados)
        empleadoslinea = [j for j in self.env.cr.fetchall()]
    
        if empleadoslinea != []:
            for linea in empleadoslinea:
                sheet.write(filas, 0, linea[0],letter1 )
                sheet.write(filas, 1, linea[1],letter1 )
                sheet.write(filas, 2, linea[2],letter1 )
                sheet.write(filas, 3, linea[3].strftime('%d/%m/%Y'),letter1 )
                sheet.write(filas, 4, linea[4].strftime('%d/%m/%Y'),letter1 )
                sheet.write(filas, 5, linea[5],number_right )
                filas+=1