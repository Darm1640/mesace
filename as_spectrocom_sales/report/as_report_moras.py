# -*- coding: utf-8 -*-
import calendar
import xlsxwriter
import pytz
from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from datetime import datetime, timedelta, date
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
    _name = 'report.as_spectrocom_sales.reporte_mora_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('LIBRO HISTORICO DE COMPRAS')
        #estilos
        titulo_filtro = workbook.add_format({'font_size': 10,'font_name': 'Lucida Sans', 'align': 'left', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo1 = workbook.add_format({'font_size': 11,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo_partner = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
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

        number_left = workbook.add_format({'font_size': 9, 'align': 'left', 'num_format': '#,##0.00', 'text_wrap': True})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True})
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

        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#A9A9A9'})

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',18, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',20, letter1)
        sheet.set_column('D:D',22, letter1)
        sheet.set_column('E:E',30, letter1)
        sheet.set_column('F:F',19, letter1)
        sheet.set_column('G:G',20, letter1)
        sheet.set_column('H:H',20, letter1)
        sheet.set_column('I:I',10, letter1)
        sheet.set_column('J:J',10, letter1)
        sheet.set_column('K:K',10, letter1)
        sheet.set_column('L:L',12, letter1)
        sheet.set_column('M:M',12, letter1)
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        sheet.merge_range('A4:J4', 'DETALLE FACTURAS EN MORA', titulo1)
        sheet.merge_range('A5:J5', start_date +' - '+ end_date, titulo2)
        sheet.write(5, 0, 'Usuario', titulo_filtro)
        sheet.write(6, 0, 'Ubicacion', titulo_filtro)
        # sheet.write(5, 2, 'Unidad de negocio:', titulo_filtro)
        sheet.write(6, 2, 'Fecha de impresion:', titulo_filtro)
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        sheet.write(6, 3, fecha_actual, number_right)
        sheet.write(6, 1, self.nombre_almacen(data['form']),titulo3)
        sheet.write(5, 1, self.nombre_cliente(data['form']),titulo3)

        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})     
        dict_clientes = []
        if data['form']['as_cliente']:
            for ids in data['form']['as_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND am.partner_id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''

        dict_almacen = []
        dict_aux = []
        if data['form']['as_almacen']:
            for ids in data['form']['as_almacen']:
                dict_almacen.append(ids)
                dict_aux.append(ids)
        if dict_almacen:
            filtro_almacen = "AND sp.location_id in "+str(dict_almacen).replace('[','(').replace(']',')')
            # filtro_almacen = "AND sl.id in "+str(dict_almacen).replace('[','(').replace(']',')')
        else:
            filtro_almacen = ''

        filastitle=7
        sheet.write(filastitle, 0, 'FECHA EMISION', tituloAzul)  
        sheet.write(filastitle, 1, 'Nº FACTURA', tituloAzul)
        sheet.write(filastitle, 2, 'FECHA VENCIMIENTO', tituloAzul)
        sheet.write(filastitle, 3, 'DÍAS MORA', tituloAzul)   
        sheet.write(filastitle, 4, 'UNIDAD DE NEGOCIO', tituloAzul)
        sheet.write(filastitle, 5, 'CÓDIGO ', tituloAzul)
        sheet.write(filastitle, 6, 'Nº OT', tituloAzul)
        sheet.write(filastitle, 7, 'NR', tituloAzul)
        sheet.write(filastitle, 8, 'BS', tituloAzul)
        sheet.write(filastitle, 9, 'SUS', tituloAzul)

        filas= 8

        # filas+=2
        consulta_cliente= ("""
            select 
            DISTINCT ON (rp.name) rp.name,
            rp.id
            from res_partner rp
            join account_move am on am.partner_id=rp.id
            where am.move_type = 'out_invoice' and am.state not in ('cancel','draft')
            """+str(filtro_clientes)+"""
            AND am.invoice_date::date BETWEEN '"""+str(data['form']['start_date'])+"""' AND '"""+str(data['form']['end_date'])+"""'
            """) 
        self.env.cr.execute(consulta_cliente)
        result_cliente= self.env.cr.fetchall()
        logging.debug(consulta_cliente)

        for clientes in result_cliente: 
            detalle_consulta = []
            text_query = ("""
                select to_char( am.invoice_date, 'DD-MM-YYYY') as fecha_emision,
                am.name as numero_fact,
                am.id as fecha_vencimiento,
                am.id as producto,
                atp.name as codigo,
                so.id as nro_ot,
                so.id as nr,
                am.amount_total as bs_usd
                from account_move  am
                left join res_partner rp on rp.id = am.partner_id
                left join sale_order so on so.name = am.invoice_origin
                left join stock_picking sp on so.name = sp.origin
                left join as_template_project atp on atp.id = so.as_template_id
                where am.move_type = 'out_invoice' and am.state not in ('cancel','draft')
                AND rp.id= '"""+str(clientes[1])+"""'
                AND am.invoice_date::date BETWEEN '"""+str(data['form']['start_date'])+"""' AND '"""+str(data['form']['end_date'])+"""'
                """ + str(filtro_almacen) + """
                """ + str(filtro_clientes) + """
                order by am.partner_id
            """)
            logging.debug(text_query)
            self.env.cr.execute(text_query)
            result= self.env.cr.fetchall()

            if result != []:
                # sheet.write(filas, 0, clientes[0], titulo2)
                sheet.merge_range('A'+str(filas+1)+':J'+str(filas+1), clientes[0], color_cabecera_plomo)

                filas +=1

            for x in result:
                product_ids = self.env['account.move.line'].search([('move_id','=',x[3])], order="name desc")
                productos = ''
                for lineas_productos in product_ids:
                    if lineas_productos.product_id.as_bussiness_id.name == False:
                        productos += ''
                    else:
                        productos = lineas_productos.product_id.as_bussiness_id.name 
                        continue
                # dias de mora 
                factura = self.env['account.move'].search([('id','=',x[2])])
                if factura.as_fecha_vencimiento:
                    vencimientos = datetime.strptime(str(factura.as_fecha_vencimiento),'%Y-%m-%d').strftime('%d-%m-%Y')
                    diferencia = datetime.now()- factura.create_date
                    # vencimiento = datetime.fromisoformat(factura.as_fecha_vencimiento)
                    vencimiento = diferencia.days
                else:
                    vencimiento = ' '
                currency_bob = self.env['res.currency'].search([('id','=',62)])
                currency_us = self.env['res.currency'].search([('id','=',2)])
                if factura.currency_id == currency_bob:
                    monto_us = x[7]
                    monto_bob = factura.currency_id._convert(x[7], currency_us, factura.company_id, factura.date)
                if factura.currency_id == currency_us:
                    monto_us = factura.currency_id._convert(x[7], currency_bob, factura.company_id, factura.date)
                    monto_bob = x[7]
                    

                # OT
                venta = self.env['sale.order'].search([('id','=',x[5])])
                tareas = self.env['project.task'].search([('sale_order_id','=',venta.id)])
                ots = ''
                nrs = ''
                for lineas_de_tarea in tareas:
                    if lineas_de_tarea.as_ot == False:
                        ots += ' '
                    else:
                        ots += ' - ' + lineas_de_tarea.as_ot + ' - '
                    nr = self.env['as.request.materials'].search([('as_project_id','=',lineas_de_tarea.id)])
                    # for nrs_asociados in nr:
                    if nr:
                        for valorado in nr:
                            nrs += str(valorado.name)+ ' '
                    else:
                        nrs += ' '
                vals ={
                    'fecha_emision':x[0],
                    'numero_fact':x[1],
                    'fecha_vencimiento':vencimientos,
                    'mora':vencimiento,
                    'producto':productos,
                    'codigo': x[4],
                    'nro_ot': ots,
                    'nr': nrs,
                    'bs': monto_bob,
                    'usd': monto_us,
                    
                }
                detalle_consulta.append(vals)
        
            # filas_aux = 10
            for item in detalle_consulta:
                sheet.write(filas, 0, item['fecha_emision'], number_left)
                sheet.write(filas, 1, item['numero_fact'], number_right)
                sheet.write(filas, 2, item['fecha_vencimiento'], number_right)
                
                sheet.write(filas, 3, item['mora'], number_right)
                sheet.write(filas, 4, item['producto'], number_right)
                sheet.write(filas, 5, item['codigo'], number_right)
                sheet.write(filas, 6, item['nro_ot'], number_right)
                sheet.write(filas, 7, item['nr'], number_right)
                sheet.write(filas, 8, item['usd'], number_right)
                sheet.write(filas, 9, item['bs'], number_right)
                # sheet.write(filas, 10, item['cliente'], number_right)
                filas+=1
                # filas_aux += 1

    def nombre_almacen(self,data):
        dict_aux = []
        dict_almacen = []
        almacen=data['as_almacen']
        if almacen:
            for line in almacen:
                dict_almacen.append('('+str(line)+')')
                dict_aux.append(line)
        filtro_almacenes_name = 'Todos'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name

    def nombre_cliente(self,data):
        dict_aux = []
        almacen=data['as_cliente']
        if almacen:
            for line in almacen:
                dict_aux.append(line)
        filtro_almacenes_name = 'Varios'
        for y in dict_aux:
            almacen_obj = self.env['res.partner'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['res.partner'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name