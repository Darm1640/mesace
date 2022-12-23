# # -*- coding: utf-8 -*-
# import calendar
# import xlsxwriter
# import pytz
# from dateutil.relativedelta import relativedelta
# from odoo import models,fields,api
# from datetime import datetime, timedelta
# from time import mktime
# from datetime import date, datetime
# import time
# from datetime import datetime, timedelta
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
# class as_cuadro_depresiciones_xlsx(models.AbstractModel):
#     _name = 'report.as_bo_assets.reporte_siat_xlsx.xlsx'
#     _inherit = 'report.report_xlsx.abstract'
    
#     def generate_xlsx_report(self, workbook, data, lines):
#         sheet = workbook.add_worksheet('LIBRO HISTORICO DE COMPRAS')
#         #estilos
#         titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
#         titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
#         tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
#         titulo3 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })
#         titulo3_number = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
#         titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
#         titulo10 =  workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
#         titulo5 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
#         titulo9 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
#         titulo6 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
#         titulo12 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
#         titulo7 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
#         titulo8 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})

#         number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00'})
#         number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00'})
#         number_right_bold = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
#         number_right_col = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
#         number_center = workbook.add_format({'font_size': 9, 'align': 'center', 'num_format': '#,##0.00'})
#         number_right_col.set_locked(False)

#         letter1 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
#         letter2 = workbook.add_format({'font_size': 9, 'align': 'left', 'bold':True})
#         letter3 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True,'font_size': 11,'font_name': 'Lucida Sans',})
#         letter4 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
#         letter4C = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True,'color': '#000000','bg_color': '#F4F5F5','font_name': 'Lucida Sans', })
#         letter4F = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True,'color': '#FFFFFF','bg_color': '#507AAA','font_name': 'Lucida Sans',})
#         letter4G = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bold': True,'color': '#000000'})
#         letter4S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
#         letter41S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
#         letter41Sr = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True,'color': 'red'})
#         letter_locked = letter3
#         letter_locked.set_locked(False)

#         # Aqui definimos en los anchos de columna
#         sheet.set_column('A:A',18, letter1)
#         sheet.set_column('B:B',25, letter1)
#         sheet.set_column('C:C',20, letter1)
#         sheet.set_column('D:D',22, letter1)
#         sheet.set_column('E:E',30, letter1)
#         sheet.set_column('F:F',19, letter1)
#         sheet.set_column('G:G',15, letter1)
#         sheet.set_column('H:H',10, letter1)
#         sheet.set_column('I:I',10, letter1)
#         sheet.set_column('J:J',10, letter1)
#         sheet.set_column('K:K',10, letter1)
#         sheet.set_column('L:L',12, letter1)
#         sheet.set_column('M:M',12, letter1)
#         start_date = str(data['form']['start_date'])
#         end_date = str(data['form']['end_date'])
#         sheet.merge_range('A4:E4', 'REPORTE SIAT', titulo1)
#         sheet.merge_range('A5:E5', start_date +' - '+ end_date, titulo2)
#         url = image_data_uri(self.env.user.company_id.logo)
#         image_data = BytesIO(urlopen(url).read())
#         sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})     
#         fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
#         filastitle=9
#         sheet.write(filastitle, 0, 'ITEM', tituloAzul)  
#         sheet.write(filastitle, 1, 'DETALLE', tituloAzul)
#         sheet.write(filastitle, 2, 'CANTIDAD', tituloAzul)
#         sheet.write(filastitle, 3, 'VALOR NETO', tituloAzul)   
#         sheet.write(filastitle, 4, 'IMPORTE BAJAS', tituloAzul)
        
#         sheet.write(0, 3, 'NIT: ', titulo10) 
#         sheet.write(0, 4, str(self.env.user.company_id.vat), titulo3)
#         sheet.write(1, 3, 'DIRECCION: ', titulo10)
#         sheet.write(1, 4, str(self.env.user.company_id.street), titulo3)
#         sheet.write(2, 3, 'CELULAR, TELEFONO:', titulo10)
#         sheet.write(2, 4, str(self.env.user.company_id.phone), titulo3) 
#         sheet.write(7, 3, 'Fecha de impresion: ', titulo4)
#         sheet.write(7, 4, fecha_actual, titulo3) 
#         sheet.write(6, 0, 'Usuario:', titulo4)
#         sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
#         sheet.write(7, 0, 'Productos: ', titulo4)
#         sheet.write(7, 1, 'Todos', titulo3)
#         filas= 8
#         periodo_struct_time_convert = time.strptime(str(data['form']['start_date']), '%Y-%m-%d')
#         periodo_time_convert = datetime.fromtimestamp(mktime(periodo_struct_time_convert))
#         periodo_traducido = self.mes_traducido(periodo_time_convert)
#         gestion = periodo_time_convert.strftime('%Y')
#         fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
#         filas+=1
#         detalle_consulta = []
#         category_ids = self.env['account.asset.category'].search([], order="name desc")
#         for cate in category_ids:
#             detalle_categ = []
#             total_cantidad = 0.0
#             total_saldo_anterior = 0.0
#             total_saldo_actual = 0.0
#             total_valor = 0.0
#             actualizacion = 0.0
#             actualizacion2 = 0.0
#             dep_acum = 0.0
#             valor_actualizacion = 0.0
#             total_actualizacion = 0.0
#             total_actualizacion2 = 0.0
#             total_valor_actualizacion = 0.0
#             total_dep_acum = 0.0
#             total_dep_actualizado = 0.0
#             dep_actualizado=0.0
#             dep_periodo=0.0
#             total_dep_periodo=0.0            
#             dep_periodo_end=0.0
#             total_dep_periodo_end=0.0            
#             dep_periodo_final=0.0
#             total_dep_periodo_final=0.0
#             dep_valor_neto=0.0
#             total_dep_valor_neto=0.0
#             product_ids = self.env['product.product'].search([('asset_category_id','=',cate.id)], order="name desc")
#             vals={}
#             for product in product_ids:
#                 cantidad = 0.0
#                 saldo_anterior = 0.0
#                 saldo_actual = 0.0
#                 saldo_valor = 0.0
#                 text_query = ("""
#                     SELECT
#                         pp.id
#                         ,sum(assl.as_value)
#                         ,sum(assl.as_value_updates)
#                         ,sum(assl.as_updates)
#                         ,sum(assl.as_value_updates)
#                         ,sum(assl.as_depreciation_store)
#                         ,sum(assl.as_update_depreciation)
#                         ,sum(assl.as_depreciation_periodo)
#                         ,sum(assl.as_depreciation_end)
#                         ,sum(assl.as_valor_neto)
#                         from account_asset_depreciation_line assl
#                         join account_asset_asset ass on ass.id = assl.asset_id
#                         join product_product pp on pp.id = ass.product_id
#                         left join account_move_line ai on ai.move_id = ass.invoice_id and ai.product_id = pp.id
#                         where
#                             pp.id = '"""+str(product.id)+"""'
#                             AND (assl.depreciation_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+"""'
#                             AND (assl.depreciation_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['end_date'])+"""'
#                         GROUP BY 1
#                 """)
#                 # assl.move_check='True'
#                 self.env.cr.execute(text_query)
#                 result= self.env.cr.fetchall()
#                 res= self._get_saldos_fechas(product.id,str(start_date),str(end_date),cate.account_depreciation_expense_id.id)
#                 cantidad = res['cantidad']
#                 saldo_anterior = res['saldo_anterior']
#                 saldo_actual = res['saldo_actual']
#                 if result:
#                     saldo_valor = float(result[0][1])
#                     actualizacion = float(result[0][2])
#                     valor_actualizacion = float(result[0][3])
#                     dep_acum = float(result[0][4])
#                     actualizacion2 = float(result[0][6])
#                     dep_actualizado = float(result[0][6])
#                     dep_periodo_end = float(result[0][7])
#                     dep_periodo_final = float(result[0][8])
#                     dep_valor_neto = float(result[0][9])
#                 #totales
#                 total_cantidad += cantidad
#                 total_saldo_anterior += saldo_anterior
#                 total_saldo_actual += saldo_actual
#                 total_valor += saldo_valor
#                 total_actualizacion += actualizacion
#                 total_valor_actualizacion += valor_actualizacion
#                 total_dep_acum += dep_acum
#                 total_actualizacion2 +=actualizacion2
#                 total_dep_actualizado += dep_actualizado
#                 total_dep_periodo_end += dep_periodo_end
#                 total_dep_periodo_final += dep_periodo_final
#                 total_dep_valor_neto += dep_valor_neto

#                 vals ={
#                     'categ':'',
#                     'default_code':product.default_code,
#                     'name':product.name,
#                     'cantidad': cantidad,
#                     'saldo_anterior': saldo_anterior,
#                     'saldo_actual': saldo_actual,
#                     'saldo_valor': saldo_valor,
#                     'actualizacion': actualizacion,
#                     'valor_actualizacion': valor_actualizacion,
#                     'dep_acum': dep_acum,
#                     'actualizacion2': actualizacion2,
#                     'dep_actualizado': dep_actualizado,
#                     'dep_periodo_end': dep_periodo_end,
#                     'dep_periodo_final': dep_periodo_final,
#                     'dep_valor_neto': dep_valor_neto,

#                 }
#                 detalle_consulta.append(vals)
    

#         for item in detalle_consulta:
#             if item['dep_valor_neto'] >= 0.0:
#                 sheet.write(filas, 0, item['default_code'], number_right)
#                 sheet.write(filas, 1, item['name'], number_left)
#                 sheet.write(filas, 2, item['cantidad'], number_right)
#                 sheet.write(filas, 3, item['dep_valor_neto'], number_right)
#                 sheet.write(filas, 4, 0.0, letter4G)
#                 filas+=1

        

    
#     def _get_saldos_fechas(self,product_id,fecha_start,fecha_end,account_id):
#         mes= (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%m')
#         anio= (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%Y')
#         year_a= (datetime.strptime(str(fecha_end), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
#         #module no callable
#         primer_dia_anterior= year_a+'-'+'01'+'-'+'01'
#         ultimo_dia_anterior= year_a+'-'+'12'+'-'+'31'
#         tuple_query = []
#         saldo_anterior = 0.0
#         cantidad = 0.0
#         saldo_actual = 0.0
#         depre_anterior = 0.0
#         #saldo_anterior
#         text_query = ("""
#             SELECT
#             pp.id b
#             ,sum(ass.value)
#             from account_asset_asset ass 
#             join product_product pp on pp.id = ass.product_id
#             left join account_move_line ai on ai.move_id = ass.invoice_id and ai.product_id = pp.id
#             left join account_move aii on aii.id = ai.move_id
#             where 
#             ass.state='open'
#             and pp.id = '"""+str(product_id)+"""'
#             AND (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(fecha_start)+"""' 
#             GROUP BY 1
#         """)
#         self.env.cr.execute(text_query)
#         res= self.env.cr.fetchall()
#         if res:
#             saldo_anterior = res[0][1]
#             depre_anterior = res[0][1]
#         #saldo actual 
#         year=  (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%Y')
#         primer_dia_actual= year+'-'+'01'+'-'+'01'
#         ultimo_dia_actual= fecha_end
#         text_query = ("""
#         SELECT
#             pp.id
#             ,sum(ai.quantity)
#             ,sum(ass.value)
#             from account_asset_asset ass 
#             join product_product pp on pp.id = ass.product_id
#             left join account_move_line ai on ai.move_id = ass.invoice_id and ai.product_id = pp.id
#             left join account_move aii on aii.id = ai.move_id
#             where 
#             ass.state='open'
#             and pp.id = '"""+str(product_id)+"""'
#             AND (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(fecha_start)+"""'
#             AND (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(fecha_end)+"""'
#             GROUP BY 1
#         """)
#         self.env.cr.execute(text_query)
#         res1= self.env.cr.fetchall()
#         if res1:
#             if res1[0][1] != None:
#                 cantidad = float(res1[0][1])
#             saldo_actual += float(res1[0][2])
            
#         vals = {
#             'cantidad': cantidad,
#             'saldo_anterior': saldo_anterior,
#             'saldo_actual': saldo_actual,
#             'depre_anterior': depre_anterior,

#         }
#         return vals

    
#     def get_rate_ufv_end(self,fecha):
#         mes= (datetime.strptime(str(fecha), '%Y-%m-%d') + relativedelta(months=1)).strftime('%m')
#         anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
#         periodo = calendar.monthrange(int(anio),int(mes))
#         primer_dia= fecha
#         primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
#         ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
#         as_ufv_actual = self.env['res.currency.rate'].search([('name', '<=', fecha),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
#         return as_ufv_actual

    
#     def get_rate_ufv_start(self,fecha):
#         mes= (datetime.strptime(str(fecha), '%Y-%m-%d') + relativedelta(months=1)).strftime('%m')
#         anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
#         periodo = calendar.monthrange(int(anio),int(mes))
#         primer_dia= fecha
#         primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
#         ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
#         as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', fecha),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
#         return as_ufv_ant

#     def mes_traducido(self,convertir_mes):
#         month = convertir_mes.strftime('%B')
#         mes = month
#         if month == 'January':
#             mes = 'Enero'
#         elif month == 'February':
#             mes = 'Febrero'
#         elif month == 'March':
#             mes = 'Marzo'
#         elif month == 'April':
#             mes = 'Abril'
#         elif month == 'May':
#             mes = 'Mayo'
#         elif month == 'June':
#             mes = 'Junio'
#         elif month == 'July':
#             mes = 'Julio'
#         elif month == 'August':
#             mes = 'Agosto'
#         elif month == 'September':
#             mes = 'Septiembre'
#         elif month == 'October':
#             mes = 'Octubre'
#         elif month == 'November':
#             mes = 'Noviembre'
#         elif month == 'December':
#             mes = 'Diciembre'
#         return mes


    
#     def lista_dosificaciones(self,data):
#         start_date = str(data['form']['start_date'])
#         end_date = str(data['form']['end_date'])
#         company_ids = self.env['res.company'].search([])
#         comapnys = []
#         contador = 1
#         for qr_code in company_ids:
#             periodo_struct_time_convert =  time.strptime(str(data['form']['start_date']), '%Y-%m-%d')
#             periodo_time_convert = datetime.fromtimestamp(mktime(periodo_struct_time_convert))
#             periodo_traducido = self.mes_traducido(periodo_time_convert)
#             gestion = periodo_time_convert.strftime('%Y')
#             dic = {
#                 'id_sucursal': qr_code.id,
#                 'periodo': periodo_traducido,
#                 'gestion': gestion,
#                 'empresa': qr_code.name,
#                 'nit_empresa': qr_code.vat,
#                 'nombre_empresa': qr_code.partner_id.name,
#                 'direccion1': qr_code.street,
#                 'direccion2': qr_code.street2,
#                 'telefono': qr_code.phone,
#                 'ciudad': str(qr_code.city) + str(qr_code.country_id.name),
#                 'descripcion_actividad': qr_code.incoterm_id.name,             
#                 'contador': contador,
#                 }
#             contador += 1
#             comapnys.append(dic)
        
#         return comapnys             


# reporte de SIAT hecho por mauricio el 7/7/2022
# -*- coding: utf-8 -*-
import calendar
import xlsxwriter
import pytz
from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from datetime import datetime, timedelta
from time import mktime
from datetime import date, datetime
import time
from datetime import datetime, timedelta
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
class as_cuadro_depresiciones_xlsx(models.AbstractModel):
    _name = 'report.as_bo_assets.reporte_siat_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('LIBRO HISTORICO DE COMPRAS')
        #estilos
        titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })
        titulo3_number = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
        titulo10 =  workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo5 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo9 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo6 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo12 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo7 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
        titulo8 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap':True})
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
        letter4S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter41S = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True})
        letter41Sr = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True,'color': 'red'})
        letter_locked = letter3
        letter_locked.set_locked(False)

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',15, letter1)
        sheet.set_column('B:B',40, letter1)
        sheet.set_column('C:C',15, letter1)
        sheet.set_column('D:D',15, letter1)
        sheet.set_column('E:E',15, letter1)
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        sheet.merge_range('A4:E4', 'REPORTE SIAT', titulo1)
        sheet.merge_range('A5:E5', start_date +' - '+ end_date, titulo2)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})     
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        
        # FILTROS
        dict_product=[] #aqui se guardan los ids del wizard
        filtro_products_po =''
        if data['form']['as_producto']:
            for line in data['form']['as_producto']:
                dict_product.append(line)
        if dict_product: 
            whe = 'AND pp.id IN'
            filtro_products_po += whe
            filtro_products_po +=str(dict_product).replace('[','(').replace(']',')')
        else:
            filtro_products_po += ''
            
        # FILTROS
        dict_lote=[] #aqui se guardan los ids del wizard
        filtro_lote =''
        if data['form']['as_lote']:
            for linea in data['form']['as_lote']:
                dict_lote.append(linea)
        if dict_lote: 
            whe = 'AND spt.id IN'
            filtro_lote += whe
            filtro_lote +=str(dict_lote).replace('[','(').replace(']',')')
        else:
            filtro_lote += ''
            
            
        filastitle=8
        sheet.write(filastitle, 0, 'ITEM', tituloAzul)  
        sheet.write(filastitle, 1, 'DETALLE', tituloAzul)
        sheet.write(filastitle, 2, 'CANTIDAD', tituloAzul)
        sheet.write(filastitle, 3, 'VALOR NETO', tituloAzul)   
        sheet.write(filastitle, 4, 'IMPORTE BAJAS', tituloAzul)
        sheet.freeze_panes(9, 0)
        sheet.write(0, 3, 'NIT: ', titulo10) 
        sheet.write(0, 4, str(self.env.user.company_id.vat), titulo3)
        sheet.write(1, 3, 'DIRECCION: ', titulo10)
        sheet.write(1, 4, str(self.env.user.company_id.street), titulo3)
        sheet.write(2, 3, 'CELULAR, TELEFONO:', titulo10)
        sheet.write(2, 4, str(self.env.user.company_id.phone), titulo3) 
        sheet.write(7, 3, 'Fecha de impresion: ', titulo4)
        sheet.write(7, 4, fecha_actual, titulo3) 
        sheet.write(6, 0, 'Usuario:', titulo4)
        sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(7, 0, 'Productos: ', titulo4)
        sheet.write(7, 1, 'Todos', titulo3)
        filas = 9
        consulta_productos= ("""
                select
                    ass.as_code_assets,
                    ass.name,
                    ass.value,
                    ass.as_amount_sale
                    from account_asset_asset as ass
                    left join product_product as pp on pp.id = ass.product_id
                    left join product_template as pt on pt.id = pp.product_tmpl_id
                    left join stock_production_lot as spt on spt.id = ass.as_lot_id

                where 
                (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+ """'
                AND (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+ """'
                """+str(filtro_products_po)+ """
                """+str(filtro_lote)+ """
                """)
        self.env.cr.execute(consulta_productos)
        productoslinea = [j for j in self.env.cr.fetchall()]
        if productoslinea != []:
            for linea in productoslinea:
                sheet.write(filas, 0, linea[0], number_right)
                sheet.write(filas, 1, linea[1], number_left)
                sheet.write(filas, 2, 1, number_right)
                sheet.write(filas, 3, linea[2], number_right)
                sheet.write(filas, 4, 0, number_right)
                filas+=1
               