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

class as_lista_activos_fijos(models.AbstractModel):
    _name = 'report.as_bo_assets.report_activos_fijos_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Reporte de Cheques')
        #estilos
        titulo1 = workbook.add_format({'font_size': 20,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
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

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_total = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True,  'bottom': True, 'top': True,'left': True, 'right': True,'bold':True})
        number_total_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_total_right_co_uno = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
        number_datos = workbook.add_format({'font_size': 9, 'align': 'right','text_wrap': True,'bold':True})
        number_right_bold = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 9, 'align': 'center','text_wrap': True, 'bottom': True, 'top': True,'left': True, 'right': True,})
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
        number_left.set_align('vcenter')
        number_total_right_co_uno.set_align('vcenter')
        number_total.set_align('vcenter')
        number_total_right.set_align('vcenter')
        number_center.set_align('vcenter')
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',16, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',20, letter1)
        sheet.set_column('D:D',28, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',20, letter1)
        sheet.set_column('H:H',20, letter1)
        sheet.set_column('I:I',28, letter1)
        sheet.set_column('J:J',28, letter1)
        sheet.set_column('K:K',20, letter1)
        sheet.set_column('L:L',12, letter1)
        sheet.set_column('M:M',12, letter1)

        # Titulos, subtitulos, filtros y campos del reporte  
        sheet.merge_range('A4:I4', 'LISTA ACTIVOS FIJOS', titulo1)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:C4', url, {'image_data': image_data,'x_scale': 0.27, 'y_scale': 0.13})     
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        filastitle=8
        
        sheet.write(0, 7, 'NIT: ', titulo3) 
        sheet.write(1, 7, 'DIRECCION: ', titulo3) 
        sheet.write(2, 7, 'CELULAR, TELEFONO:', titulo3)   
        sheet.write(5, 7, 'Fecha de impresion: ', titulo4)
        sheet.write(0, 8, self.env.user.company_id.vat, number_datos) 
        sheet.write(1, 8, self.env.user.company_id.street, number_datos) 
        sheet.write(2, 8, self.env.user.company_id.phone, number_datos) 
        sheet.write(5, 8, fecha_actual, titulo3) 
        
        
        sheet.write(5, 0, 'Usuario:', titulo4)
        sheet.write(5, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(6, 0, 'Productos:', titulo4)
        sheet.write(6, 1, self.obtneer_productos(data['form']), titulo3)
        sheet.write(6, 7, 'Serie/s:', titulo4)
        sheet.write(6, 8, self.obtneer_serie(data['form']), titulo3)
        
        
        sheet.write(filastitle, 0, 'NUMERO DE ITEMS', tituloAzul)  
        sheet.write(filastitle, 1, 'CODIGO', tituloAzul)
        sheet.write(filastitle, 2, 'CODIGO ACTIVO FIJO', tituloAzul)
        sheet.write(filastitle, 3, 'PRODUCTO', tituloAzul)   
        sheet.write(filastitle, 4, 'NRO DE SERIE', tituloAzul)   
        sheet.write(filastitle, 5, 'MARCA', tituloAzul) 
        sheet.write(filastitle, 6, 'MODELO', tituloAzul)
        sheet.write(filastitle, 7, 'NRO DE PARTE', tituloAzul)
        sheet.write(filastitle, 8, 'CATEGORIA', tituloAzul)
        sheet.write(filastitle, 9, 'VALOR', tituloAzul)
        filas= 9

        if data['form']['as_serie_lote_filter']:
            filtro_cliente ="""AND spl.id = '"""+str(data['form']['as_serie_lote_filter'])+"""'"""
        else:
            filtro_cliente = ''
            
        dict_productos = []
        if data['form']['as_producto_filter']:
            for line in data['form']['as_producto_filter']:
                dict_productos.append(line)
        if dict_productos:
            filtro_productos = "AND ass.product_id in "+str(dict_productos).replace('[','(').replace(']',')')
        else:
            filtro_productos = ''
            
        if data['form']['as_marca_filter']:
            filtro_marca ="""AND pb.id = '"""+str(data['form']['as_marca_filter'])+"""'"""
        else:
            filtro_marca = ''
            
        if data['form']['as_categoria_filter']:
            filtro_categoria ="""AND aac.id = '"""+str(data['form']['as_categoria_filter'])+"""'"""
        else:
            filtro_categoria = ''

        consulta_product= ("""
        select
            pp.default_code, 
            ass.as_code_assets,
            pt.name,
            spl.name,
            pb.name,
            pm.name,
            pt.product_part_num,
            aac.name,
            ass.value
            from account_asset_asset as ass
            left join product_product as pp on pp.id = ass.product_id
            left join product_template as pt on pt.id = pp.product_tmpl_id
            left join stock_production_lot as spl on spl.id = ass.as_lot_id
            left join product_brand as pb on pb.id = pt.product_brand_id
            left join product_model as pm on pm.id = pt.product_model_id
            left join account_asset_category as  aac on aac.id = ass.category_id
            WHERE
                ass.company_id = '1'
                """+str(filtro_cliente)+"""
                """+str(filtro_productos)+"""
                """+str(filtro_marca)+"""
                """+str(filtro_categoria)+"""
                AND (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+ """'
                AND (ass.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+ """'

        """)
        self.env.cr.execute(consulta_product)
        productos = [k for k in self.env.cr.fetchall()]
        cont=0
        total = 0.0
        if productos != []:
            for linea in productos:            
                sheet.write(filas, 0, cont, number_center )
                sheet.write(filas, 1, linea[0], number_total_right) 
                sheet.write(filas, 2, linea[1], number_total_right) 
                sheet.write(filas, 3, linea[2], number_left)   
                sheet.write(filas, 4, linea[3], number_total_right)  
                sheet.write(filas, 5, linea[4], number_left)   
                sheet.write(filas, 6, linea[5], number_left) 
                sheet.write(filas, 7, linea[6], number_total_right) 
                sheet.write(filas, 8, linea[7], number_left) 
                sheet.write(filas, 9, linea[8], number_total_right) 
                total+=linea[8]
                filas+=1
                cont+=1
        sheet.merge_range('A'+str(filas+1)+':I'+str(filas+1)+'', 'TOTAL', titulo1)
        sheet.write(filas, 9, total, number_total_right)
        
                
                
    def obtneer_productos(self,data):
        dict_aux = []
        dict_almacen = []
        almacen=data['as_producto_filter']
        if almacen:
            for ids in almacen:
                dict_almacen.append(ids)
                dict_aux.append(ids)
        nombre_del_producto = 'Todos'
        for y in dict_aux:
            id_producto = self.env['product.product'].search([('id', '=', y)], limit=1)
            nombre_producto=self.env['product.template'].search([('id', '=', id_producto.product_tmpl_id.ids)], limit=1)
            
            nombre_del_producto += ', ' + nombre_producto.name 
        # if len(dict_aux) == 1:
        #     nombre_del_producto = self.env['product.product'].search([('id', '=', dict_aux[0])], limit=1).name
        return nombre_del_producto
    
    
    def obtneer_serie(self,data):
        almacen=data['as_serie_lote_filter']
        nombre_del_producto='Todos'
        if almacen:
            id_producto = self.env['stock.production.lot'].search([('id', '=',almacen)], limit=1)
            nombre_del_producto += ', ' + id_producto.name 
        else:
            nombre_del_producto += ' '
        # if len(dict_aux) == 1:
        #     nombre_del_producto = self.env['product.product'].search([('id', '=', dict_aux[0])], limit=1).name
        return nombre_del_producto
        
        
        