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

# class a_libro_historico_xlsx(models.AbstractModel):
#     _name = 'report.as_spectrocom_repair.as_historial_reparaciones_xlsx.xlsx'
#     _inherit = 'report.report_xlsx.abstract'
    

#     def generate_xlsx_report(self, workbook, data, lines):     
#         sheet = workbook.add_worksheet('LIBRO HISTORICO DE REPARACIONES')
#         #estilos
#         titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
#         titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
#         tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
#         titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
#         titulo3_number = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
#         titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
#         titulo10 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
#         titulo5 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
#         titulo9 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
#         titulo6 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
#         titulo12 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
#         titulo7 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
#         titulo8 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})

#         number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00',  'text_wrap': True})
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
#         sheet.set_column('B:B',18, letter1)
#         sheet.set_column('C:C',20, letter1)
#         sheet.set_column('D:D',28, letter1)
#         sheet.set_column('E:E',25, letter1)
#         sheet.set_column('F:F',19, letter1)
#         sheet.set_column('G:G',15, letter1)
#         sheet.set_column('H:H',22, letter1)
#         sheet.set_column('I:I',20, letter1)
#         sheet.set_column('J:J',10, letter1)
#         sheet.set_column('K:K',10, letter1)
#         sheet.set_column('L:L',12, letter1)
#         sheet.set_column('M:M',12, letter1)

#         #defincion de filtros para reportes
 
     
#         fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
#         fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
#         dict_product=[] #aqui se guardan los ids del wizard
        
#         # Titulos, subtitulos, filtros y campos del reporte  
#         sheet.merge_range('A4:I4', 'HISTORIAL DE REPARACIONES', titulo1)
#         sheet.merge_range('A5:I5', fecha_inicial +' - '+ fecha_final, titulo2)
#         url = image_data_uri(self.env.user.company_id.logo)
#         image_data = BytesIO(urlopen(url).read())
#         sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.16})     
#         fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
#         filastitle=9
#         sheet.write(filastitle, 0, 'ITEM', tituloAzul)  
#         sheet.write(filastitle, 1, 'FECHA INGRESO', tituloAzul)
#         sheet.write(filastitle, 2, 'CLIENTE', tituloAzul)
#         sheet.write(filastitle, 3, 'PRODUCTO', tituloAzul)   
#         sheet.write(filastitle, 4, 'CATEGORIA', tituloAzul)   
#         sheet.write(filastitle, 5, 'Nº SERIE', tituloAzul) 
#         sheet.write(filastitle, 6, 'DIAGNOSTICO', tituloAzul)
#         sheet.write(filastitle, 7, 'REPARACION', tituloAzul)
#         sheet.write(filastitle, 8, 'FECHA SALIDA', tituloAzul) 
#         sheet.write(0, 7, 'NIT: ', titulo3) 
#         sheet.write(1, 7, 'DIRECCION: ', titulo3) 
#         sheet.write(2, 7, 'CELULAR, TELEFONO:', titulo3)   
#         sheet.write(6, 7, 'Fecha de impresion: ', titulo4)
#         sheet.write(6, 8, fecha_actual, titulo3) 
#         sheet.write(7, 7, 'Productos:', titulo4)
#         sheet.write(7, 8, 'Todos:', titulo3)
#         sheet.write(6, 0, 'Usuario:', titulo4)
#         sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
#         sheet.write(7, 0, 'Cliente:', titulo4)
#         sheet.write(7, 1, 'todos:', titulo3)
#         filas= 10
#         # Preparando variables para cada casod e consulta
#         #consultas
#         dict_lot = []
#         if data['form']['as_series']:
#             for ids in data['form']['as_series']:
#                 dict_lot.append(ids)
#         if dict_lot:
#             filtro_lote = "AND spl.id in "+str(dict_lot).replace('[','(').replace(']',')')
#         else:
#             filtro_lote = ''
#         consulta_product= ("""
                
#                 select 
#                     ro.name as "item",
#                     to_char((( ro.create_date AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) AS "fecha_ingreso",
#                     rp.name as "cliente",
#                     pt.name as "producto",
#                     ro.id,
#                     spl.name as "lote",
#                     ro.internal_notes as "diagnostico",
#                     ro.quotation_notes as "reparacion",
#                     to_char((( sp.date_done AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) AS "fecha_salida"
#                     from repair_order ro
#                     left join res_partner rp on rp.id=ro.partner_id
#                     left join product_product pp on pp.id=ro.product_id
#                     left join product_template pt on pt.id=pp.product_tmpl_id
#                     left join repair_line rl on rl.id=ro.id
#                     left join stock_production_lot spl on spl.id=rl.lot_id
#                     left join stock_picking sp on  sp.origin=ro.name
                    
#                     WHERE
                    
#                         (ro.create_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+"""'
#                         AND (ro.create_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+"""'
#                         """+str(filtro_lote)+"""
                        
#                 """)
#         self.env.cr.execute(consulta_product)
#         productos = [k for k in self.env.cr.fetchall()]
#         if productos != []:
#             for produ in productos:
#                 cons=("""select rt.name from repair_order_repair_tags_rel rortl join repair_tags rt on rortl.     repair_tags_id=rt.id
#                     WHERE rortl.repair_order_id="""+str(produ[4])+""" """)
#                 self.env.cr.execute(cons)
#                 categoria = [k for k in self.env.cr.fetchall()]
#                 categoriprodu=''
#                 for linea in categoria:
#                     categoriprodu+=linea[0]+''
                    
#                 sheet.write('A'+str(filas+1),produ[0],number_left)
#                 sheet.write('B'+str(filas+1),produ[1],number_right)
#                 sheet.write('C'+str(filas+1),produ[2],number_left)
#                 sheet.write('D'+str(filas+1),produ[3],number_left)
#                 sheet.write('E'+str(filas+1),categoriprodu,number_left)
#                 sheet.write('F'+str(filas+1),produ[5],number_right)
#                 sheet.write('G'+str(filas+1),produ[6],number_left)
#                 sheet.write('H'+str(filas+1),produ[7],number_left)
#                 sheet.write('I'+str(filas+1),produ[8],number_right)
#                 filas+=1
                