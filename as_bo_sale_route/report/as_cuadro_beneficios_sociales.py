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
    _name = 'report.as_bo_sale_route.as_cuadro_beneficios_sociales_xlsx.xlsx'
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
        number_left_totales = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00','bg_color':'#A9A9A9','bold':True })
        number_right_totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color':'#A9A9A9','bold':True })

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
        letter4 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True})
        letter_locked = letter3
        letter_locked.set_locked(True)
        totales_Azul = workbook.add_format({'font_size': 12, 'align': 'right', 'bold':True,'bg_color':'#F0F8FF'})
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        sheet.set_column('A:N',10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',8, letter1)
        sheet.set_column('B:B',20, letter1)
        sheet.set_column('C:C',35, letter1) 
        sheet.set_column('D:D',35, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',20, letter1)
        sheet.set_column('H:H',8, letter1)
        sheet.set_column('I:I',8, letter1)
        sheet.set_column('J:J',8, letter1)
        sheet.set_column('K:K',20, letter1)

        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:B5', url, {'image_data': image_data,'x_scale': 0.28, 'y_scale': 0.17})

        sheet.merge_range('G1:I1', 'NIT: ', titulo3) 
        sheet.merge_range('G2:I2', 'DIRECCION: ', titulo3) 
        sheet.merge_range('G3:I3', 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('J1:K1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('J2:K2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('J3:K3', str(self.env.user.company_id.phone), titulo3derecha)

        sheet.merge_range('A5:K5', 'CUADRO DE BENEFICIOS SOCIALES', titulo1)
        
        sheet.write(7, 1, 'Usuario: ', titulo4)
        sheet.write(7, 2, str(self.env.user.partner_id.name), titulo3)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y')
        sheet.merge_range('H8:J8', 'Fecha de impresion: ', titulo4)
        sheet.write(7, 10, fecha, titulo3)

        sheet.write(9, 0, 'No.', titulo2) 
        sheet.write(9, 1, 'C.I', titulo2) 
        sheet.write(9, 2, 'APELLIDOS Y NOMBRE', titulo2) 
        sheet.write(9, 3, 'FECHA DE INGRESO', titulo2)  
        sheet.write(9, 4, 'FECHA ULTIMO PAGO FINIQUITO', titulo2)  
        sheet.write(9, 5, 'TOTAL GANADO ENERO', titulo2) 
        sheet.write(9, 6, 'PROMEDIO', titulo2) 
        sheet.write(9, 7, 'A', titulo2)
        sheet.write(9, 8, 'M', titulo2) 
        sheet.write(9, 9, 'D', titulo2) 
        sheet.write(9, 10, 'PREVISION', titulo2)  


        dict_product=[] #aqui se guardan los ids del wizard
        
        
        filtro_products_po =''
        if data['form']['as_nombre_empleado']:
            for line in data['form']['as_nombre_empleado']:
                dict_product.append(line)
        if dict_product: 
            whe = 'AND hrc.employee_id IN'
            filtro_products_po += whe
            filtro_products_po +=str(dict_product).replace('[','(').replace(']',')')
        else:
            filtro_products_po += ''

        consulta_empleados= ("""
               select 
                DISTINCT(hre.name),
                    hre.identification_id,
                    hre.as_expedito,
                    hre.name, 
                    hrc.date_start,
                    hrf.as_date_end,
                    hrpl.total
                from hr_contract as hrc
                left join hr_employee as hre on hre.id = hrc.employee_id
				left join as_hr_finiquito as hrf on hrf.employee_id = hre.id
				left join hr_payslip_line as hrpl on hrpl.employee_id = hre.id 
                where hrpl.name = 'Total Ganado'AND hrc.active = True
                """+str(filtro_products_po)+ """
                """)

        filas= 10
        self.env.cr.execute(consulta_empleados)
        empleadoslinea = [j for j in self.env.cr.fetchall()]
        
        empleadoslinea2 = []
        for j in  empleadoslinea:
            if j not in empleadoslinea2:
                empleadoslinea2.append(j)
    
        cont=0
        total=0
        totalp=0
        date_h = data['form']['fecha']
        fecha_hoy = datetime.strptime(date_h, '%Y-%m-%d')
        sheet.merge_range('A6:K6','AL '+  date_h, tituloAzul)
        if empleadoslinea2 != []:
                for linea in empleadoslinea2:
                        if linea[1] == None:
                            num = ""
                        else:
                            num = str(linea[1])
                        if linea[2] == None:    
                            ex = ""
                        else:
                            ex = str(linea[2])
                        if linea[3] == None:
                            nom = ""
                        else:
                            nom = str(linea[3])
                        if linea[5] == None:
                            fecha_ini = linea[4].strftime('%d/%m/%Y')
                            fecha_finiquito=""
                        else:
                            fecha_ini = linea[5].strftime('%d/%m/%Y')
                            fecha_finiquito=linea[5].strftime('%d/%m/%Y')
                        cont +=1
                        ci = num + " " + ex
                        
                        fecha_fin = fecha_hoy.strftime('%d/%m/%Y')
                        date_ini = datetime.strptime(fecha_ini, '%d/%m/%Y')  
                        date_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')
                        tiempo = (date_fin - date_ini)
                        dias = int((tiempo.days/30/12 - int(tiempo.days/30/12))*30)
                        meses = int((tiempo.days/30/12 - int(tiempo.days/30/12))*12)

                        if int(tiempo.days/30/12) >= 1:
                            años = int(tiempo.days/30/12)
                        else:
                            años = 0

                        sheet.write(filas, 0, cont,letter1 )
                        sheet.write(filas, 1, ci,letter1 )
                        sheet.write(filas, 2, nom,letter1 )
                        sheet.write(filas, 3, linea[4].strftime('%d/%m/%Y'),letter4 )
                        sheet.write(filas, 4, fecha_finiquito,letter4 )
                        sheet.write(filas, 5, linea[6],number_right )
                        sheet.write(filas, 6, linea[6],number_right )
                        sheet.write(filas, 7, años,letter4 )
                        sheet.write(filas, 8, meses,letter4 )
                        sheet.write(filas, 9, dias,letter4 )
                        promedio = linea[6]
                        prevision = (promedio*años)+(promedio/12*meses)+(promedio/12/30*dias)
                        sheet.write(filas, 10, prevision,number_right )
                    
                        
                        totalp += prevision               
                        total += linea[6]
                        filas += 1

        sheet.merge_range('C'+str(filas+1)+':D'+str(filas+1), 'Total: ', number_left_totales)  
        sheet.write(filas, 4, '',number_right_totales )    
        sheet.write(filas, 5, total,number_right_totales )
        sheet.write(filas, 6, total,number_right_totales )
        sheet.write(filas, 7, '',number_right_totales ) 
        sheet.write(filas, 8, '',number_right_totales ) 
        sheet.write(filas, 9, '',number_right_totales ) 
        sheet.write(filas, 10, totalp,number_right_totales )   
        