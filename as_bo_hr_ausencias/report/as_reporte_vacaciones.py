# # -*- coding: utf-8 -*-
import time
from openpyxl.styles import Alignment
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
from io import BytesIO
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo.tools.image import image_data_uri
import math
import locale
from urllib.request import urlopen
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class as_reporte_vacacion(models.AbstractModel):
    _name = 'report.as_bo_hr_ausencias.as_reporte_vacaciones_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Reporte de vacaciones')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4', 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'left', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo1_debajo = workbook.add_format({'font_size': 15, 'align': 'center', 'text_wrap': True,'top': False, 'bold':True, 'bottom': True })

        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 10, 'align': 'left', 'num_format': '#,##0.00', 'text_wrap': True, 'bottom': True, 'top': True, })
        number_left_totales = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00','bg_color':'#A9A9A9' })
        number_right_totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color':'#A9A9A9' })

        
        number_right = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, })
        number_right_lineas = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, })
        
        number_right_col = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        
        number_right_col.set_locked(False)
        
        letter1 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True})
        
        letter3 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True})
        
        letter_locked = letter3
        letter_locked.set_locked(True)
        
        titulo2.set_align('vcenter')
        sheet.set_column('A:N',10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',20, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',20, letter1)
        sheet.set_column('D:D',20, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',20, letter1)
        sheet.set_column('H:H',20, letter1)
        sheet.set_column('I:I',20, letter1)

        # url = image_data_uri(self.env.user.company_id.logo)
        # image_data = BytesIO(urlopen(url).read())
        # sheet.insert_image('A1:B5', url, {'image_data': image_data,'x_scale': 0.28, 'y_scale': 0.17})

        sheet.merge_range('A2:H2', 'VACACIONES ACUMULADAS POR PERIODO (EN DIAS)', titulo1)
        dict_empleado=[] #aqui se guardan los ids del wizard
        filtro_empleados_po =''
        if data['form']['as_nombre_empleado']:
            for line in data['form']['as_nombre_empleado']:
                dict_empleado.append(line)
        if dict_empleado: 
            whe = 'AND he.id IN'
            filtro_empleados_po += whe
            filtro_empleados_po +=str(dict_empleado).replace('[','(').replace(']',')')
        else:
            filtro_empleados_po += ''

        if data['form']['as_departamento']:
            filtro_departure ="""AND hdep.id = '"""+str(data['form']['as_departamento'])+"""'"""
        else:
            filtro_departure = ''
        
        consulta_empleados= ("""
                select 
                he.name,
                he.job_title,
                he.as_fecha_ingreso,
                he.id
                from hr_employee as he
                left join hr_department as hdep on hdep.id = he.department_id
                where 
                he.company_id = '1'
                """+str(filtro_departure)+ """
                """+str(filtro_empleados_po)+ """
                """)

        filas= 3
        self.env.cr.execute(consulta_empleados)
        empleadoslinea = [j for j in self.env.cr.fetchall()]
        total=0.0
        contador = 0
        if empleadoslinea != []:
            for linea in empleadoslinea:
                sheet.write(filas, 0, 'Empleado: ', titulo4)
                sheet.write(filas, 1, linea[0],number_left )
                sheet.write(filas, 2, 'Cargo: ', titulo4)
                sheet.write(filas, 3, linea[1],number_left )
                sheet.write(filas, 4, 'Fecha de Ingreso: ', titulo4)
                sheet.write(filas, 5, linea[2].strftime('%Y-%m-%d'),number_right )
                sheet.write(filas, 6, 'Dias Resumen: ', titulo4)
                sheet.write(filas, 7, self.as_get_dias_disponibles(int(linea[3])),number_right )
                if data['form']['as_detallado'] == True:
                    sheet.merge_range('A'+str(filas+2)+':B'+str(filas+2), 'GESTION', titulo2)
                    sheet.merge_range('C'+str(filas+2)+':D'+str(filas+2), 'ACUMULADOS', titulo2)
                    sheet.merge_range('E'+str(filas+2)+':F'+str(filas+2), 'UTILIZADOS', titulo2)
                    sheet.merge_range('G'+str(filas+2)+':H'+str(filas+2), 'DISPONIBLE', titulo2)
                    filas_linea = filas+2
                    if linea[3]:
                        if self.as_get_periodos(int(linea[3])):
                            for y in self.as_get_periodos(int(linea[3])):
                                sheet.write(filas_linea, 0, y['as_date_from'],number_right_lineas )
                                sheet.write(filas_linea, 1, y['as_date_to'].strftime('%Y-%m-%d'),number_right_lineas )
                                sheet.write(filas_linea, 3, y['as_disponible'],number_right_lineas )
                                sheet.write(filas_linea, 5, y['as_usado'],number_right_lineas )
                                total = int(y['as_disponible']) - int(y['as_usado'])
                                sheet.write(filas_linea, 7, total,number_right_lineas )
                                filas_linea +=1
                            
                    filas= filas_linea + 1
                else:
                    filas+=1
       
    def as_get_dias_disponibles(self, id_empleado):
        id_vacaciones = self.env['hr.employee'].sudo().search([('id','=',id_empleado)])
        dias_acumulados = 0
        dias_usados = 0
        if id_vacaciones:
            for ausencia in id_vacaciones:
                now = datetime.now()
                if not ausencia.as_fecha_ingreso:
                    raise UserError(_('Debe completar fecha de ingreso en empleado'))
                fecha_ingreso = ausencia.as_fecha_ingreso
                antiguedad = fecha_ingreso - now
                dias = int(antiguedad.days/30/12)*-1
                for dia in range(1,dias):
                    if dia < 5:
                        dias_acumulados+= 15
                    else:
                        dias_acumulados+= 20
                solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',ausencia.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
                dias_usados = 0.0
                var_aux = 0.0
                if solicitudes:
                    for day in solicitudes:
                        dias_usados += day.number_of_days
                var_aux = dias_acumulados-dias_usados
                    # como puedo hacer cuadno hay 2 solciitudes de vacaciones
            return var_aux
    
    def as_get_periodos(self,data):
        id_vacaciones = self.env['hr.employee'].sudo().search([('id','=',data)])
        dias_acumulados = 0
        dias_usados = 0
        for ausencia in id_vacaciones:
            now = datetime.now()
            valores = []
            if not ausencia.as_fecha_ingreso:
                raise UserError(_('Debe completar fecha de ingreso en empleado'))
            fecha_ingreso = ausencia.as_fecha_ingreso
            antiguedad = fecha_ingreso - now
            dias = int(antiguedad.days/30/12)*-1
            cont = 0
            fecha_i = ausencia.as_fecha_ingreso
            for dia in range(1,dias):
                if dia < 5:
                    vals = {
                        'as_date_from': fecha_i.strftime('%Y-%m-%d'),
                        'as_disponible': 15,
                        'as_leave': ausencia.id,
                        'as_usado':0
                    }
                    fecha_i = fecha_i + relativedelta(years=1)
                    vals['as_date_to'] = fecha_i
                    valores.append(vals)
                    dias_acumulados+= 15 
                    
                else:
                    vals = {
                        'as_date_from': fecha_i.strftime('%Y-%m-%d'),
                        'as_disponible': 20,
                        'as_leave': ausencia.id,
                        'as_usado':0
                    }
                    fecha_i = fecha_i + relativedelta(years=1)
                    vals['as_date_to'] = fecha_i
                    valores.append(vals)
                    dias_acumulados+= 20
            
            # lines = self.env['as.hr.periodo'].sudo().create(valores)       
            solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',ausencia.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
            dias_usados = 0.0
            var_aux = dias_acumulados
            if solicitudes:
                for day in solicitudes:
                    dias_usados += day.number_of_days
                dias_utilizados = dias_usados
                for line in valores:
                    if float(dias_utilizados) >= float(line['as_disponible']):
                        line['as_usado']  = float(line['as_disponible'])
                        dias_utilizados -= float(line['as_disponible'])
                    else:
                        line['as_usado']  = float(dias_utilizados)
                        dias_utilizados -= dias_utilizados  
            # ausencia.as_disponible = dias_acumulados-dias_usados
            return valores