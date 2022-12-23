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
    _name = 'report.as_bo_purchase_reports.as_libro_historico.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('LIBRO HISTORICO DE COMPRAS')
        #estilos
        titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
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
        dict_product=[] #aqui se guardan los ids del wizard
        filtro_products_po =''
        if data['form']['as_productos']:
            for line in data['form']['as_productos']:
                dict_product.append(line)
        if dict_product: 
            whe = 'where pp.id IN'
            filtro_products_po += whe
            filtro_products_po +=str(dict_product).replace('[','(').replace(']',')')
        else:
            filtro_products_po += ''
        
        
        # Titulos, subtitulos, filtros y campos del reporte  
        sheet.merge_range('A4:F4', 'HISTORICO DE COMPRA DE PRODUCTOS', titulo1)
        sheet.merge_range('A5:F5', fecha_inicial +' - '+ fecha_final, titulo2)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})     
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        filastitle=9
        sheet.write(filastitle, 0, 'PRODUCTO', tituloAzul)  
        sheet.write(filastitle, 1, 'PROVEEDOR', tituloAzul)
        sheet.write(filastitle, 2, 'COMPRA', tituloAzul)
        sheet.write(filastitle, 3, 'FECHA DE COMPRA', tituloAzul)   
        sheet.write(filastitle, 4, 'P.U.', tituloAzul)   
        sheet.write(filastitle, 5, 'DIFERENCIA', tituloAzul) 
        sheet.write(0, 4, 'NIT: ', titulo3) 
        sheet.write(1, 4, 'DIRECCION: ', titulo3) 
        sheet.write(2, 4, 'CELULAR, TELEFONO:', titulo3)   
        sheet.write(7, 4, 'Fecha de impresion: ', titulo4)
        sheet.write(7, 5, fecha_actual, titulo3) 
        sheet.write(6, 0, 'Usuario:', titulo4)
        sheet.write(6, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(7, 0, 'Productos: ', titulo4)
        sheet.write(7, 1, 'Todos', titulo3)
        filas= 10
        # Preparando variables para cada casod e consulta
        #consultas
        consulta_productos= ("""
                SELECT name,pp.id FROM product_product pp 
                join product_template pt on pp.product_tmpl_id = pt.id """ + str(filtro_products_po) + """ WHERE type='product'
                """)
        self.env.cr.execute(consulta_productos)
        vec=[]
        cont=0
        aux=0
        productos = [k for k in self.env.cr.fetchall()]
        for produ in productos:
            consulta_product= ("""
                SELECT display_name,(date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT'),price_unit, po.name FROM purchase_order_line pol
                join purchase_order po on po.id = pol.order_id
                join res_partner rp on po.partner_id = rp.id WHERE pol.product_id = """ + str(produ[1]) + """
                and (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+ """'
                AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+ """' ORDER BY date_order asc
                """)
            self.env.cr.execute(consulta_product)
            productoslinea = [j for j in self.env.cr.fetchall()]
            if productoslinea != []:
                sheet.merge_range('A'+str(filas+1)+':F'+str(filas+1), produ[0], letter4C)
                filas+=1
                vec=[]
                cont=0
                for vector in productoslinea:
                    vec.append(vector[2])
                    cont=len(vec)
                conta=cont
                aux=conta
                for linea in reversed(productoslinea):
                    conta=conta-1
                    if conta<=0:
                        sheet.write('F'+str(filas+1), 0, letter4G)
                    else:
                        resta=round(vec[conta]-vec[conta-1],1)
                        sheet.write('F'+str(filas+1), resta, letter4G)
                    sheet.write('B'+str(filas+1), linea[0], letter4G)
                    sheet.write('C'+str(filas+1), linea[3], letter4G)
                    sheet.write('D'+str(filas+1), linea[1].strftime('%d/%m/%Y %H:%M:%S'), letter4G)
                    sheet.write('E'+str(filas+1), linea[2], letter4G)
                    filas+=1

            
        
    
                