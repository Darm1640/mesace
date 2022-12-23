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
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
class as_cuadro_depresiciones_xlsx(models.AbstractModel):
    _name = 'report.as_spectrocom_sales.reporte_siat_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('LIBRO HISTORICO DE COMPRAS')
        #estilos
        titulo1 = workbook.add_format({'font_size': 20,'font_name': 'Lucida Sans', 'align': 'center', 'text_wrap': True, 'bold':True,'color': '#4682B4' })
        titulo2 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })
        
        titulo4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
        

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00','text_wrap': True})
        number_id = workbook.add_format({'font_size': 12, 'align': 'center','text_wrap': True})
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True})
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

        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#A9A9A9','text_wrap': True})
        color_cabecera_plomo2=workbook.add_format({'font_size': 12, 'align': 'right','bg_color':'#A9A9A9','num_format': '#,##0.00','text_wrap': True})

        letter_locked = letter3
        letter_locked.set_locked(False)
        tituloAzul.set_align('vcenter')
        color_cabecera_plomo2.set_align('vcenter')
        number_left.set_align('vcenter')
        number_right.set_align('vcenter')
        number_id.set_align('vcenter')
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',25, letter1)
        sheet.set_column('B:B',15, letter1)
        sheet.set_column('C:C',10, letter1)
        sheet.set_column('D:D',15, letter1)
        sheet.set_column('E:E',15, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',15, letter1)
        sheet.set_column('H:H',30, letter1)
        sheet.set_column('I:I',20, letter1)
        sheet.set_column('J:J',20, letter1)
        sheet.set_column('K:K',20, letter1)
        sheet.set_column('L:L',16, letter1)
        sheet.set_column('M:M',16, letter1)
        sheet.set_column('N:N',16, letter1)
        sheet.set_column('O:O',20, letter1)
        sheet.set_column('P:P',16, letter1)
        sheet.set_column('Q:Q',16, letter1)
        sheet.set_column('R:R',16, letter1)
        sheet.set_column('S:S',16, letter1)
        sheet.set_column('T:T',16, letter1)
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        sheet.merge_range('A4:Q4', 'REPORTE CONTROL DE PRE FACTURA Y FACTURAS', titulo1)
        sheet.merge_range('A5:Q5', start_date +' - '+ end_date, titulo2)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A4', url, {'image_data': image_data,'x_scale': 0.25, 'y_scale': 0.12})     
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        dict_clientes = []
        # if data['form']['as_cliente']:
        #     for ids in data['form']['as_cliente']:
        #         dict_clientes.append(ids)
        # if dict_clientes:
        #     filtro_clientes = "AND so.partner_id in "+str(dict_clientes).replace('[','(').replace(']',')')
        #     filtro_clientes_so = "AND am.partner_id in "+str(dict_clientes).replace('[','(').replace(']',')')
        # else:
        #     filtro_clientes = ''
        #     filtro_clientes_so= ''
        sheet.write(6, 0, 'Fecha de impresion:', titulo4)

        sheet.write(7, 0, 'Clientes:', titulo4)
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        sheet.write(6, 1, fecha_actual, number_right)
        sheet.write(7, 1, 'TODOS',titulo3)
        filastitle=8

        sheet.write(filastitle, 0, 'CLIENTE', tituloAzul) 
        sheet.write(filastitle, 1, 'ID PREFACTURA', tituloAzul)
        sheet.write(filastitle, 2, 'NUMERO DE FACTURA', tituloAzul)  
        sheet.write(filastitle, 3, 'PERIODOS DE FATURACIÓN', tituloAzul)
        sheet.write(filastitle, 4, 'ESTADO', tituloAzul)
        sheet.write(filastitle, 5, 'REF. CLIENTE', tituloAzul)
        sheet.write(filastitle, 6, 'CANTIDAD', tituloAzul) 
        sheet.write(filastitle, 7, 'PRODUCTO Y/O SERVICIO', tituloAzul)
        sheet.write(filastitle, 8, 'CÓDIGO', tituloAzul)
        # sheet.write(filastitle, 9, 'SUB LINEA DE NEGOCIO', tituloAzul)
        sheet.write(filastitle, 9, 'ESTADO DE SERVICIO', tituloAzul)
        # sheet.write(filastitle, 11, 'SEGUIMIENTO ALQUILER', tituloAzul)
        sheet.write(filastitle, 10, 'DIAS DE MORA FACTURA', tituloAzul)
        sheet.write(filastitle, 11, 'FECHA FACTURA', tituloAzul)
        # sheet.write(filastitle, 14, 'ACTIVIDAD ECONOMICA', tituloAzul)
        sheet.write(filastitle, 12, 'COMPROBANTE DIARIO', tituloAzul)
        sheet.write(filastitle, 13, 'TOTALFACTURADO', tituloAzul)
        sheet.write(filastitle, 14, 'MONTO PAGADO', tituloAzul)
        sheet.write(filastitle, 15, 'SALDO DEUDOR', tituloAzul)
        sheet.write(filastitle, 16, 'FECHA DE PAGO', tituloAzul)
        
        filas= 8
        filas+=1

        consulta_cliente= ("""
            select 
            DISTINCT ON (rp.name) rp.name,
            rp.id
            from res_partner rp
            left join account_move am on am.partner_id=rp.id
            where am.move_type = 'out_invoice'
            AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >='"""+str(data['form']['start_date'])+"""' 
            AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <='"""+str(data['form']['end_date'])+"""'
            """) 
        self.env.cr.execute(consulta_cliente)
        result_cliente= self.env.cr.fetchall()
        logging.debug(consulta_cliente)

        for clientes in result_cliente: 
            detalle_consulta = []
            text_query = ("""
                    select rp.name as cliente,
                    am.narration as periodos,
                    am.as_etapa as estado,
                    am.ref as referencia,
                    am.id,
                    atp.name as codigo,
                    apt.name,
                    am.invoice_date as fecha_factura,
                    am.name as numero_factura,
                    am.amount_total as total_facturado,
                    so.as_pagado as total_pagado,
                    so.id,
                    am.as_invoice_number,
                    am.id,
                    am.invoice_payment_term_id
                    from account_move am
                    left join sale_order so on so.name = am.invoice_origin
                    left join res_partner rp on rp.id = am.partner_id
                    left join as_template_project atp on so.as_template_id = atp.id
                    left join account_payment_term apt on so.payment_term_id = apt.id
                    where am.move_type = 'out_invoice' AND am.state in ('posted','draft','Regularizar')
                    AND rp.id= '"""+str(clientes[1])+"""'
                    AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+"""'
                    AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+"""'
            """)
            logging.debug(text_query)
            self.env.cr.execute(text_query)
            result= self.env.cr.fetchall()
            
            for x in result:
                vals ={
                    'cliente':x[0],
                    'periodos':x[1],
                    'estado':x[2],
                    'referencia': x[3],
                    'cantidad': x[4],
                    'codigo': x[5],
                    'mora': x[6],
                    'fecha_factura': x[7],
                    'no_factura': x[8],
                    'total_facturado': x[9],
                    'total_pagado': x[10],
                    'so': x[11],
                    'id_factura':x[13],
                    'as_invoice_number':x[12],
                    'account_payment_term_id':x[14]

                }
                detalle_consulta.append(vals)
        
            tot_fact = 0
            tot_pagado = 0
            tot_deuda = 0
            for item in detalle_consulta:
                as_suscripcion = ''
                as_seguimiento = ''
                if item['so'] != None:
                    sale_order = self.env['sale.order'].search([('id','=',str(item['so']))])
                    # as_seguimiento = sale_order.subscription_management
                    for sol in sale_order.order_line:
                        if sol.subscription_id:
                            as_suscripcion += sol.subscription_id.stage_id.name + ' '

                moves = self.env['account.move'].search([('id','=',str(item['cantidad']))])
                pagos = moves.get_payment()
                cantidad = 0
                productos = ''
                sublinea = ''
                unidad_negocio = ''
                pago_bs = 0.0
                for lineas in moves.invoice_line_ids:
                    cantidad += lineas.quantity
                    productos += lineas.name + ' - '
                    if lineas.product_id:
                        if lineas.product_id.categ_id.name != False and lineas.product_id.as_type_id.name != False:
                            sublinea += str(lineas.product_id.categ_id.name) +' '+ str(lineas.product_id.as_type_id.name)+','
                        else:
                            if lineas.product_id.categ_id.name != False:
                                sublinea += ' '+ str(lineas.product_id.categ_id.name)+','
                            else:
                                if lineas.product_id.as_type_id.name != False:
                                    sublinea += ' '+ str(lineas.product_id.as_type_id.name)+','
                                else:
                                    sublinea += ' '
                    # if lineas.product_id.product_tmpl_id.as_type_id:
                        # sublinea += lineas.product_id.product_tmpl_id.as_type_id.name
                    if lineas.product_id.product_tmpl_id.as_bussiness_id:
                        unidad_negocio += lineas.product_id.product_tmpl_id.as_bussiness_id.name

                if pagos:
                    for pays in pagos:
                        almacen_obj = self.env['account.move'].search([('id', '=',item['id_factura'])])
                        valores_concatenados=''
                        if almacen_obj.as_conditions_lines:
                            lineas_proposales = self.env['as.proposal.conditions.sale'].search([('id', '=',almacen_obj.as_conditions_lines.ids)])
                            for captura in lineas_proposales:
                                if captura.name and captura.as_valor!=False:
                                    valores_concatenados += ' - '+(str(captura.name) +': '+str(captura.as_valor)+' - ')
                        sheet.write(filas, 0, item['cliente'], number_left)
                        sheet.write(filas, 1, item['id_factura'], number_id)
                        sheet.write(filas, 2, item['as_invoice_number'], number_id)
                        sheet.write(filas, 3, item['periodos'], number_left)
                        sheet.write(filas, 4, item['estado'], number_left)
                        sheet.write(filas, 5, valores_concatenados, number_left)
                        sheet.write(filas, 6, cantidad, number_right)
                        sheet.write(filas, 7, str(productos), number_left)
                        sheet.write(filas, 8, item['codigo'], number_left)
                        # sheet.write(filas, 9, str(sublinea), number_left)
                        sheet.write(filas, 9, as_suscripcion, number_left)
                        # sheet.write(filas, 11, as_seguimiento, number_left)
                        fecha_hoy=datetime.strftime(datetime.now() ,'%Y-%m-%d %H:%M:%S')
                        fecha_fact=item['fecha_factura'].strftime('%Y-%m-%d %H:%M:%S')
                        formato='%Y-%m-%d %H:%M:%S'
                        d1=datetime.strptime(fecha_hoy,formato)
                        d2=datetime.strptime(fecha_fact,formato)
                        dif=d2-d1
                        resta_dias=dif.days
                        # sheet.write(filas, 12, item['mora'], number_right)
                        paaggoos = self.env['account.payment.term'].search([('id', '=',item['account_payment_term_id'])])
                        para_restar=0
                        if paaggoos:
                            if paaggoos.name == '15 Días':
                                para_restar=15
                            if paaggoos.name == '30 Días':
                                para_restar=30
                            if paaggoos.name == '45 Días':
                                para_restar=45
                            if paaggoos.name == '90 Días':
                                para_restar=90
                            if paaggoos.name == '21 Días':
                                para_restar=21
                            if paaggoos.name == '2 Meses':
                                para_restar=60
                        sheet.write(filas, 10, resta_dias  , number_id)
                        sheet.write(filas, 11, item['fecha_factura'].strftime('%d/%m/%Y') , number_right)
                        # sheet.write(filas, 14, str(unidad_negocio), number_left)
                        sheet.write(filas, 12, item['no_factura'], number_right)
                        sheet.write(filas, 13, item['total_facturado'], number_right)
                        sheet.write(filas, 14, pays.amount, number_right)
                        if item['total_facturado'] == None:
                            tot1 = 0
                        else:
                            tot1 = float(item['total_facturado'])
                        if pays.amount == None:
                            tot2 = 0
                        else:
                            tot2 = float(pays.amount)

                        sheet.write(filas, 15, tot1-tot2, number_right)

                        # sheet.write_formula(filas, 16,('O'+str(filas+1)+'-P'+str(filas+1)), number_right) # SUBTOTAL
                        id_invoice = self.env['account.move'].search([('id','=',item['id_factura'])])
                        diario=0.0
                        diario_str=''
                        fecha=''
                        if id_invoice:
                            for pagos in id_invoice.get_payment():
                                if pagos.date:
                                   fecha = (pagos.date).strftime('%d/%m/%Y')
                                else:
                                    fecha=''
                        sheet.write(filas, 16,fecha, number_right)
                        if item['total_facturado']:
                            tot_fact += item['total_facturado']
                        if  pays.amount:
                            tot_pagado += pays.amount
                        tot_deuda += tot1-tot2
                        filas+=1

                else:
                    sheet.write(filas, 0, item['cliente'], number_left)
                    sheet.write(filas, 1, item['id_factura'], number_id)
                    sheet.write(filas, 2, item['as_invoice_number'], number_id)
                    sheet.write(filas, 3, item['periodos'], number_left)
                    sheet.write(filas, 4, item['estado'], number_left)
                    almacen_obj = self.env['account.move'].search([('id', '=',item['id_factura'])])
                    valores_concatenados=''
                    if almacen_obj.as_conditions_lines:
                        lineas_proposales = self.env['as.proposal.conditions.sale'].search([('id', '=',almacen_obj.as_conditions_lines.ids)])
                        for captura in lineas_proposales:
                            if captura.name and captura.as_valor!=False:
                                valores_concatenados += ' - '+(str(captura.name) +': '+str(captura.as_valor)+' - ')
                    sheet.write(filas, 5, valores_concatenados, number_left)
                    sheet.write(filas, 6, cantidad, number_right)
                    sheet.write(filas, 7, str(productos), number_left)
                    sheet.write(filas, 8, item['codigo'], number_left)
                    # sheet.write(filas, 9, str(sublinea), number_left)
                    sheet.write(filas, 9, as_suscripcion, number_left)
                    # sheet.write(filas, 11, as_seguimiento, number_left)
                    
                    fecha_hoy=datetime.strftime(datetime.now() ,'%Y-%m-%d %H:%M:%S')
                    fecha_fact=item['fecha_factura'].strftime('%Y-%m-%d %H:%M:%S')
                    formato='%Y-%m-%d %H:%M:%S'
                    d1=datetime.strptime(fecha_hoy,formato)
                    d2=datetime.strptime(fecha_fact,formato)
                    dif=d1-d2
                    resta_dias=dif.days
                    # sheet.write(filas, 12, item['mora'], number_right)
                    paaggoos = self.env['account.payment.term'].search([('id', '=',item['account_payment_term_id'])])
                    para_restar=0
                    if paaggoos:
                        if paaggoos.name == '15 Días':
                            para_restar=15
                        if paaggoos.name == '30 Días':
                            para_restar=30
                        if paaggoos.name == '45 Días':
                            para_restar=45
                        if paaggoos.name == '90 Días':
                            para_restar=90
                        if paaggoos.name == '21 Días':
                            para_restar=21
                        if paaggoos.name == '2 Meses':
                            para_restar=60
                    sheet.write(filas, 10, resta_dias, number_id)
                    sheet.write(filas, 11, item['fecha_factura'].strftime('%d/%m/%Y') , number_right)
                    # sheet.write(filas, 14, str(unidad_negocio), number_left)
                    sheet.write(filas, 12, item['no_factura'], number_right)
                    sheet.write(filas, 13, item['total_facturado'], number_right)
                    sheet.write(filas, 14, 0.0, number_right)
                    if item['total_facturado'] == None:
                        tot1 = 0
                    else:
                        tot1 = float(item['total_facturado'])
                    tot2 = 0
                    sheet.write(filas, 15, tot1-tot2, number_right)
                    id_invoice = self.env['account.move'].search([('id','=',item['id_factura'])])
                    diario=0.0
                    diario_str=''
                    fecha=''
                    if id_invoice:
                        for pagos in id_invoice:
                            fecha = (pagos.invoice_date).strftime('%d/%m/%Y')
                        # for pagos in id_invoice.get_payment():
                        #     if pagos.date:
                        #         fecha = (pagos.date).strftime('%d/%m/%Y')
                        #     else:
                        #         fecha=''
                        
                    sheet.write(filas, 16, fecha, number_right)
                    if item['total_facturado']:
                        tot_fact += item['total_facturado']
                    tot_deuda += tot1-tot2
                    filas+=1
            if result != []:
                sheet.merge_range('A'+str(filas+1)+':P'+str(filas+1), clientes[0], color_cabecera_plomo)
                sheet.write(filas,13, tot_fact, color_cabecera_plomo2)
                sheet.write(filas,14, tot_pagado, color_cabecera_plomo2)
                sheet.write(filas,15, tot_deuda, color_cabecera_plomo2)
                sheet.write(filas,16, '', color_cabecera_plomo)
                filas +=1

 