# import datetime
# import xlsxwriter
# from datetime import datetime
# import pytz
# from odoo import models,fields
# from datetime import datetime, timedelta
# from time import mktime
# from dateutil import relativedelta
# import time
# import locale
# import operator
# import itertools
# from datetime import datetime, timedelta
# from dateutil import relativedelta
# import xlwt
# from xlsxwriter.workbook import Workbook
# from odoo.tools.translate import _
# import base64
# from io import BytesIO
# from odoo.tools.image import image_data_uri
# import locale
# from odoo import netsvc
# from odoo import tools
# from urllib.request import urlopen
# from time import mktime
# import logging
# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)

# class as_report_vacaciones_pdf(models.AbstractModel):
#     _name = 'report.as_bo_hr_ausencias.as_report_vacations_pdf'
#     _inherit = 'report.report_xlsx.abstract'
    
#     def _get_report_values(self, docids, data=None):
#         if not data.get('form'):
#             raise UserError(_("Form content is missing, this report cannot be printed."))
#         return {
#                 'fecha_actual' : self._fecha_actual(),
#                 'lista_salidas_inventarios' : self.generate_xlsx_report(data),
#                 'logo':self.env.user.company_id.logo,
#                 'usuario':self.env.user.partner_id.name,
#                 }

#     def generate_xlsx_report(self,data):     
#         dict_empleado=[] #aqui se guardan los ids del wizard
#         filtro_empleados_po =''
#         if data['form']['as_nombre_empleado']:
#             for line in data['form']['as_nombre_empleado']:
#                 dict_empleado.append(line)
#         if dict_empleado: 
#             whe = 'AND he.id IN'
#             filtro_empleados_po += whe
#             filtro_empleados_po +=str(dict_empleado).replace('[','(').replace(']',')')
#         else:
#             filtro_empleados_po += ''

#         if data['form']['as_departamento']:
#             filtro_departure ="""AND hdep.id = '"""+str(data['form']['as_departamento'])+"""'"""
#         else:
#             filtro_departure = ''
        
#         consulta_empleados= ("""
#                 select 
#                 he.name,
#                 he.job_title,
#                 he.as_fecha_ingreso,
#                 he.id,
#                 hl.id
#                 from hr_leave as hl
#                 left join hr_employee as he on he.id = hl.employee_id
#                 left join hr_department as hdep on hdep.id = he.department_id
#                 where 
#                 he.company_id = '1'
#                 """+str(filtro_departure)+ """
#                 """+str(filtro_empleados_po)+ """
#                 """)

#         filas= 3
#         self.env.cr.execute(consulta_empleados)
#         empleadoslinea = [j for j in self.env.cr.fetchall()]
#         total=0.0
#         if empleadoslinea != []:
#             for linea in empleadoslinea:
#                 sheet.write(filas, 0, 'Empleado: ', titulo4)
#                 sheet.write(filas, 1, linea[0],number_left )
#                 sheet.write(filas, 2, 'Cargo: ', titulo4)
#                 sheet.write(filas, 3, linea[1],number_left )
#                 sheet.write(filas, 4, 'Fecha de Ingreso: ', titulo4)
#                 sheet.write(filas, 5, linea[2].strftime('%Y-%m-%d'),number_right )
#                 sheet.write(filas, 6, 'Dias Resumen: ', titulo4)
#                 sheet.write(filas, 7, self.as_get_dias_disponibles(linea[4]),number_right )
#                 if data['form']['as_detallado'] == True:
#                     sheet.merge_range('A'+str(filas+2)+':B'+str(filas+2), 'GESTION', titulo2)
#                     sheet.merge_range('C'+str(filas+2)+':D'+str(filas+2), 'ACUMULADOS', titulo2)
#                     sheet.merge_range('E'+str(filas+2)+':F'+str(filas+2), 'UTILIZADOS', titulo2)
#                     sheet.merge_range('G'+str(filas+2)+':H'+str(filas+2), 'DISPONIBLE', titulo2)
#                     filas_linea = filas
#                     if linea[4]:
#                         for y in self.as_get_periodos(linea[4]):
#                             sheet.write(filas_linea+2, 0, y['as_date_from'],number_right_lineas )
#                             sheet.write(filas_linea+2, 1, y['as_date_to'].strftime('%Y-%m-%d'),number_right_lineas )
#                             sheet.write(filas_linea+2, 3, y['as_disponible'],number_right_lineas )
#                             sheet.write(filas_linea+2, 5, y['as_usado'],number_right_lineas )
#                             total = int(y['as_disponible']) - int(y['as_usado'])
#                             sheet.write(filas_linea+2, 7, total,number_right_lineas )
#                             filas_linea +=1

#                 filas+=1
       
#     def as_get_dias_disponibles(self, data):
#         id_vacaciones = self.env['hr.leave'].sudo().search([('id','=',data)])
#         dias_acumulados = 0
#         dias_usados = 0
#         if id_vacaciones:
#             for ausencia in id_vacaciones:
#                 if ausencia.holiday_status_id.as_calculo_vaca or ausencia.as_vaca_permiso:
#                     now = datetime.now()
#                     if not ausencia.employee_id.as_fecha_ingreso:
#                         raise UserError(_('Debe completar fecha de ingreso en empleado'))
#                     fecha_ingreso = ausencia.employee_id.as_fecha_ingreso
#                     antiguedad = fecha_ingreso - now
#                     dias = int(antiguedad.days/30/12)*-1
#                     for dia in range(1,dias):
#                         if dia < 5:
#                             dias_acumulados+= 15
#                         else:
#                             dias_acumulados+= 20
#                     solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',ausencia.employee_id.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
#                     for day in solicitudes:
#                         dias_usados += day.number_of_days
#                     ausencia.as_disponible = dias_acumulados-dias_usados
#                 return ausencia.as_disponible
    
#     def as_get_periodos(self,data):
#         id_vacaciones = self.env['hr.leave'].sudo().search([('id','=',data)])
#         dias_acumulados = 0
#         dias_usados = 0
#         for ausencia in id_vacaciones:
#             if ausencia.holiday_status_id.as_calculo_vaca or ausencia.as_vaca_permiso:
#                 now = datetime.now()
#                 ausencia.as_periodos_ids.unlink()
#                 valores = []
#                 if not ausencia.employee_id.as_fecha_ingreso:
#                     raise UserError(_('Debe completar fecha de ingreso en empleado'))
#                 fecha_ingreso = ausencia.employee_id.as_fecha_ingreso
#                 antiguedad = fecha_ingreso - now
#                 dias = int(antiguedad.days/30/12)*-1
#                 cont = 0
#                 fecha_i = ausencia.employee_id.as_fecha_ingreso
#                 for dia in range(1,dias):
#                     if dia < 5:
#                         vals = {
#                             'as_date_from': fecha_i.strftime('%Y-%m-%d'),
#                             'as_disponible': 15,
#                             'as_leave': ausencia.id,
#                             'as_usado':0
#                         }
#                         fecha_i = fecha_i + relativedelta(years=1)
#                         vals['as_date_to'] = fecha_i
#                         valores.append(vals)
#                         dias_acumulados+= 15 
                        
#                     else:
#                         vals = {
#                             'as_date_from': fecha_i.strftime('%Y-%m-%d'),
#                             'as_disponible': 20,
#                             'as_leave': ausencia.id,
#                             'as_usado':0
#                         }
#                         fecha_i = fecha_i + relativedelta(years=1)
#                         vals['as_date_to'] = fecha_i
#                         valores.append(vals)
#                         dias_acumulados+= 20
                
#                 # lines = self.env['as.hr.periodo'].sudo().create(valores)       
#                 solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',ausencia.employee_id.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
#                 for day in solicitudes:
#                     dias_usados += day.number_of_days
#                 dias_utilizados = dias_usados
#                 for line in valores:
#                     if dias_utilizados >= ausencia.as_disponible:
#                         line['as_usado']  = ausencia.as_disponible
#                         dias_utilizados -= ausencia.as_disponible
#                     else:
#                         line['as_usado']  = dias_utilizados
#                         dias_utilizados -= dias_utilizados  
#                 # ausencia.as_disponible = dias_acumulados-dias_usados
#                 return valores