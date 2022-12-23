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

class as_resumen_cuentas_cobrar(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.as_resumen_cuentas_cobrar_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Resumen de Cuentas Cobrar')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'text_wrap': True,'bottom': True, 'top': True, 'right': True, 'left': True, })
        letra_subvalores = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00','bg_color':'#F0FFFF','bold':True, 'bottom': True, 'top': True, 'right': True, 'left': True, })
        number_subtitulos=workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True })
        totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  'bold':True })
        totales_valores = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  })
        number_days=workbook.add_format({'font_size': 12, 'align': 'center','text_wrap': True,'bottom': True, 'top': True, 'right': True, 'left': True, })
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True,'bottom': True, 'top': True, 'right': True, 'left': True, })
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'center', 'bold':True,'bg_color':'#A9A9A9','num_format': '#,##0.00', 'text_wrap': True,})

        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(True)
        totales_Azul = workbook.add_format({'font_size': 12, 'align': 'right', 'bold':True,'bg_color':'#F0F8FF'})
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        number_days.set_align('vcenter')
        number_left.set_align('vcenter')
        number_right.set_align('vcenter')
        sheet.set_column('A:N',10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',16, letter1)
        sheet.set_column('B:B',16, letter1)
        sheet.set_column('C:C',12, letter1)
        sheet.set_column('D:D',12, letter1)
        sheet.set_column('E:E',28, letter1)
        sheet.set_column('F:F',18, letter1)
        sheet.set_column('G:G',18, letter1)
        sheet.set_column('H:H',18, letter1)
        sheet.set_column('I:I',18, letter1)
        sheet.set_column('J:J',18, letter1)
        sheet.set_column('K:K',18, letter1)
        sheet.set_column('L:L',18, letter1)
        sheet.set_column('M:M',18, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:L5', 'RESUMEN DE CUENTAS POR COBRAR', titulo1)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['fecha_inicial']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['fecha_final']), '%Y-%m-%d').strftime('%d/%m/%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.38, 'y_scale': 0.17})
        # sheet.write(7, 0, 'Tipo de Producto', titulo4)
        # sheet.merge_range('B8:C8', self.tipo_producto(data['form']), titulo3)
        sheet.write(8, 0, 'Usuario', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        # sheet.write(9, 0, 'Almacen', titulo4)
        # sheet.write(9, 1, self.nombre_almacen(data['form']),titulo3)
        # sheet.write(7, 10, 'Ciudad: ', titulo4)
        # sheet.merge_range('L8:M8', self.nombre_ciudad(data['form']), titulo3)
        sheet.write(8, 10, 'Clientes: ', titulo4)
        sheet.merge_range('L9:M9', self.nombre_cliente(data['form']), titulo3)
        sheet.write(9, 10, 'Fecha de impresion: ', titulo4)
        sheet.write(9, 11, fecha, titulo3)
        sheet.merge_range('A6:L6', ' DE ['+ fecha_inicial +'] A [' + fecha_final + ']', tituloAzul)
        sheet.write(0, 9, 'NIT: ', titulo3) 
        sheet.write(1, 9, 'DIRECCION: ', titulo3) 
        sheet.write(2, 9, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('K1:L1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('K2:L2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('K3:L3', str(self.env.user.company_id.phone), titulo3derecha) 
        
        sheet.merge_range('A12:B12', 'NOMBRE', titulo2) 
        sheet.merge_range('C12:E12', 'NIT', titulo2) 
        sheet.merge_range('F12:G12', 'CIUDAD', titulo2) 
        sheet.merge_range('H12:I12', 'TELEFONO', titulo2) 
        sheet.merge_range('J12:K12', 'TOTAL BS', titulo2) 
        sheet.write(11, 11, 'TOTAL $', titulo2)
        filas = 12
        filastitle=filas
        dict_clientes = []
        if data['form']['nombre_cliente']:
            for ids in data['form']['nombre_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND rp.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''
        
        # clientes
        for cliente in dict_clientes:
            id_cliente = int(str(cliente).replace('(','').replace(')',''))
            cliente_obj = self.env['res.partner'].search([('id', '=', id_cliente)])
            nombre_cliente_report=cliente_obj.name
            sheet.merge_range('A'+str(filastitle+1)+':B'+str(filastitle+1), nombre_cliente_report, color_cabecera_plomo)
            if cliente_obj.vat != False:
                sheet.merge_range('C'+str(filastitle+1)+':E'+str(filastitle+1), cliente_obj.vat, color_cabecera_plomo)
            else:
                sheet.merge_range('C'+str(filastitle+1)+':E'+str(filastitle+1), '', color_cabecera_plomo)
            sheet.merge_range('F'+str(filastitle+1)+':G'+str(filastitle+1), cliente_obj.state_id.name, color_cabecera_plomo)
            if cliente_obj.phone != False:
                sheet.merge_range('H'+str(filastitle+1)+':I'+str(filastitle+1), cliente_obj.phone, color_cabecera_plomo)
            else:
                if cliente_obj.mobile != False:
                    sheet.merge_range('H'+str(filastitle+1)+':I'+str(filastitle+1), cliente_obj.mobile, color_cabecera_plomo)
                else:
                    sheet.merge_range('H'+str(filastitle+1)+':I'+str(filastitle+1), '', color_cabecera_plomo)
            # sheet.merge_range('K'+str(filastitle+1)+':L'+str(filastitle+1), '0', color_cabecera_plomo)
            # sheet.write(filastitle, 12, 'val', color_cabecera_plomo)
            sheet.write(filas+1, 0, 'Fecha Cred.', letra_subvalores)
            sheet.write(filas+1, 1, 'Fecha Venc.', letra_subvalores)
            sheet.write(filas+1, 2, 'Divisa', letra_subvalores)
            sheet.write(filas+1, 3, 'Dia Ven', letra_subvalores)
            sheet.write(filas+1, 4, 'Descripcion', letra_subvalores)
            # sheet.write(filas+1, 5, 'Importe', letra_subvalores)
            sheet.write(filas+1, 5, '0-30 Dias', letra_subvalores)
            sheet.write(filas+1, 6, '31-60 Dias', letra_subvalores)
            sheet.write(filas+1, 7, '61-90 Dias', letra_subvalores)
            sheet.write(filas+1, 8, '91-120 Dias', letra_subvalores)
            sheet.write(filas+1, 9, '> 120 Dias', letra_subvalores)
            sheet.write(filas+1, 10, 'Total Saldo', letra_subvalores)
            sheet.write(filas+1, 11, 'Total saldo $', letra_subvalores)
            
            
            
            filas+=1
            #consuilta de fechas creditos
            consulta_cliente_servicio= ("""
            select 
            rp.name as "cliente",
            to_char(((am.invoice_date AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) as  "fecha credito",
            to_char(((am.invoice_date_due AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) as  "fecha vencimiento",
            rc.name as "bob o usd",
            am.name as "nombre_factura",atp.name as "nombre_proyecto",am.ref as "ref cliente",
            am.amount_total as "monto factura total",
            CASE 
                WHEN apt.name = 'Immediate Payment' THEN 'Pago inmediato'
                WHEN apt.name = '21 Days' THEN '21 Dias'
                WHEN apt.name = '15 Days' THEN '15 Dias'
                WHEN apt.name = '30 Days' THEN '30 Dias'
                WHEN apt.name = '45 Days' THEN '45 Dias'
                WHEN apt.name = '2 Months' THEN '2 Meses'
                WHEN apt.name = 'End of Following Month' THEN 'Fin de Mes Siguiente'
                WHEN apt.name = '30% Now, Balance 60 Days' THEN '30% Ahora, Balance 60 Días'
            END as "forma de pago",
            am.amount_residual as "importe adeudado",
            am.invoice_date,
            am.as_invoice_number,
            am.invoice_payment_term_id
            from account_move as am
            left join res_currency as rc on rc.id = am.currency_id
            left join sale_order as so on so.name = am.invoice_origin
            left join as_template_project as atp on atp.id = so.as_template_id
            left join account_payment_term as apt on apt.id = so.payment_term_id
            left join res_partner as rp on rp.id = am.partner_id
            where am.move_type = 'out_invoice' AND am.payment_state = 'not_paid' AND am.state != 'draft'
            AND am.amount_residual > 0 AND (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['fecha_inicial'])+ """' AND
            (am.invoice_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['fecha_final'])+ """'
            """+str(filtro_clientes)+"""
            ORDER BY am.invoice_date desc
            """)
            self.env.cr.execute(consulta_cliente_servicio)
            querys_servicio = [j for j in self.env.cr.fetchall()] 
            total_bob=0
            total_usd=0
            for linea_servicio in querys_servicio:
                sheet.write(filas+1, 0, linea_servicio[1], number_right)
                sheet.write(filas+1, 1, linea_servicio[2], number_right)
                sheet.write(filas+1, 2, linea_servicio[3], number_days)

                if linea_servicio[4] != None:
                    if linea_servicio[5] != None:
                        if linea_servicio[6] != None:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4, str(linea_servicio[11]) +'/'+str(linea_servicio[4]) +'/' + str(linea_servicio[5]) +'/'+ str(linea_servicio[6]), number_right)
                            else:
                                sheet.write(filas+1, 4, str(linea_servicio[4]) +'/' + str(linea_servicio[5]) +'/'+ str(linea_servicio[6]), number_right)
                        else:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4, str(linea_servicio[11]) +'/'+str(linea_servicio[4]) +'/' + str(linea_servicio[5]), number_right)
                    else:
                        if linea_servicio[6] != None:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4, str(linea_servicio[11]) +'/'+str(linea_servicio[4]) +'/'+ str(linea_servicio[6]), number_right)
                            else:
                                sheet.write(filas+1, 4, str(linea_servicio[4]) +'/'+ str(linea_servicio[6]), number_right)
                        else:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4,str(linea_servicio[11]) +'/'+ str(linea_servicio[4]), number_right)
                            else:
                                sheet.write(filas+1, 4, str(linea_servicio[4]), number_right)
                else:
                    if linea_servicio[5] != None:
                        if linea_servicio[6] != None:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4,str(linea_servicio[11]) +'/'+ str(linea_servicio[5]) +'/'+ str(linea_servicio[6]), number_right)
                            else:
                                sheet.write(filas+1, 4,str(linea_servicio[5]) +'/'+ str(linea_servicio[6]), number_right)
                        else:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4,str(linea_servicio[11]) +'/'+ str(linea_servicio[5]), number_right)
                            else:
                                sheet.write(filas+1, 4,str(linea_servicio[5]), number_right)
                    else:
                        if linea_servicio[6] != None:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4, str(linea_servicio[11]) +'/'+str(linea_servicio[6]), number_right)
                            else:
                                sheet.write(filas+1, 4, str(linea_servicio[6]), number_right)
                        else:
                            if linea_servicio[11] != None:
                                sheet.write(filas+1, 4, str(linea_servicio[11]), number_right)
                            else:
                                sheet.write(filas+1, 4, '', number_right)
                
                # sheet.write(filas+1, 5, linea_servicio[7], number_right)#aki es descripcion
                fecha_hoy=datetime.strftime(datetime.now() ,'%Y-%m-%d %H:%M:%S')
                fecha_fact=linea_servicio[10].strftime('%Y-%m-%d %H:%M:%S')
                formato='%Y-%m-%d %H:%M:%S'
                d1=datetime.strptime(fecha_hoy,formato)
                d2=datetime.strptime(fecha_fact,formato)
                dif=d1-d2
                resta_dias=dif.days
                # # sheet.write(filas, 12, item['mora'], number_right)
                # paaggoos = self.env['account.payment.term'].search([('id', '=',linea_servicio[12].id)])
                paaggoos = linea_servicio[12]
                para_restar=0
                if paaggoos:
                    if paaggoos == 1:
                        para_restar=0
                    if paaggoos == 2:
                        para_restar=15
                    if paaggoos == 3:
                        para_restar=21
                    if paaggoos == 4:
                        para_restar=30
                    if paaggoos == 5:
                        para_restar=45
                    if paaggoos == 6:
                        para_restar=60
                    if paaggoos == 7:
                        para_restar=60
                    if paaggoos == 8:
                        para_restar=75
                    if paaggoos == 9:
                        para_restar=60
                # mora=resta_dias-para_restar
                # # sheet.write(filas+1, 3,mora , number_right)#dias para vencer
                # if mora < 0:
                #     sheet.write(filas+1, 5,linea_servicio[7], number_right)
                #     sheet.write(filas+1, 6,'', number_right)
                #     sheet.write(filas+1, 7,'', number_right)
                #     sheet.write(filas+1, 8,'', number_right)
                #     sheet.write(filas+1, 9,'', number_right)
                # if mora >=0 and mora <=30:
                #     sheet.write(filas+1, 5,linea_servicio[7], number_right)
                #     sheet.write(filas+1, 6,'', number_right)
                #     sheet.write(filas+1, 7,'', number_right)
                #     sheet.write(filas+1, 8,'', number_right)
                #     sheet.write(filas+1, 9,'', number_right)
                # if mora >=31 and mora <=60:
                #     sheet.write(filas+1, 5,'', number_right)
                #     sheet.write(filas+1, 6,linea_servicio[7], number_right)
                #     sheet.write(filas+1, 7,'', number_right)
                #     sheet.write(filas+1, 8,'', number_right)
                #     sheet.write(filas+1, 9,'', number_right)
                # if mora >=61 and mora <=90:
                #     sheet.write(filas+1, 5,'', number_right)
                #     sheet.write(filas+1, 6,'', number_right)
                #     sheet.write(filas+1, 7,linea_servicio[7], number_right)
                #     sheet.write(filas+1, 8,'', number_right)
                #     sheet.write(filas+1, 9,'', number_right)
                # if mora >=91 and mora <=120:
                #     sheet.write(filas+1, 5,'', number_right)
                #     sheet.write(filas+1, 6,'', number_right)
                #     sheet.write(filas+1, 7,'', number_right)
                #     sheet.write(filas+1, 8,linea_servicio[7], number_right)
                #     sheet.write(filas+1, 9,'', number_right)
                # if mora >121:    
                #     sheet.write(filas+1, 5,'', number_right)
                #     sheet.write(filas+1, 6,'', number_right)
                #     sheet.write(filas+1, 7,'', number_right)
                #     sheet.write(filas+1, 8,'', number_right)
                #     sheet.write(filas+1, 9,linea_servicio[7], number_right)
                sheet.write(filas+1, 3, resta_dias  , number_days)
                if linea_servicio[8] == 'Pago inmediato' or linea_servicio[8] == None:
                    sheet.write(filas+1, 5,linea_servicio[7], number_right)
                    sheet.write(filas+1, 6,'', number_right)
                    sheet.write(filas+1, 7,'', number_right)
                    sheet.write(filas+1, 8,'', number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == '21 Dias':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,linea_servicio[7], number_right)
                    sheet.write(filas+1, 7,'', number_right)
                    sheet.write(filas+1, 8,'', number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == '15 Dias':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,linea_servicio[7], number_right)
                    sheet.write(filas+1, 7,'', number_right)
                    sheet.write(filas+1, 8,'', number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == '30 Dias':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,linea_servicio[7], number_right)
                    sheet.write(filas+1, 7,'', number_right)
                    sheet.write(filas+1, 8,'', number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == '45 Dias':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,'', number_right)
                    sheet.write(filas+1, 7,linea_servicio[7], number_right)
                    sheet.write(filas+1, 8,'', number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == '2 Meses':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,'', number_right)
                    sheet.write(filas+1, 7,linea_servicio[7], number_right)
                    sheet.write(filas+1, 8,'', number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == 'Fin de Mes Siguiente':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,'', number_right)
                    sheet.write(filas+1, 7,'', number_right)
                    sheet.write(filas+1, 8,linea_servicio[7], number_right)
                    sheet.write(filas+1, 9,'', number_right)
                if linea_servicio[8] == '30% Ahora, Balance 60 Días':
                    sheet.write(filas+1, 5,'', number_right)
                    sheet.write(filas+1, 6,'', number_right)
                    sheet.write(filas+1, 7,'', number_right)
                    sheet.write(filas+1, 8,linea_servicio[7], number_right)
                    sheet.write(filas+1, 9,'', number_right)

                if linea_servicio[3] == 'BOB':
                    sheet.write(filas+1, 10, linea_servicio[9], number_right)
                    total_bob+=linea_servicio[9]
                if linea_servicio[3] == 'USD':
                    sheet.write(filas+1, 10, linea_servicio[9]*6.96, number_right)
                    total_bob+=linea_servicio[9]*6.96
                sheet.write(filas+1, 11, '', number_right)
                filas +=1
            sheet.merge_range('J'+str(filastitle+1)+':K'+str(filastitle+1), total_bob, color_cabecera_plomo)
            sheet.write(filastitle, 11, total_usd, color_cabecera_plomo)
        
    
    
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
        almacen=data['nombre_cliente']
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
    
    def nombre_ciudad(self,data):
        dict_aux = []
        almacen=data['as_ciudad']
        if almacen:
            for line in almacen:
                dict_aux.append(line)
        filtro_almacenes_name = 'Varios'
        for y in dict_aux:
            almacen_obj = self.env['res.country.state'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['res.country.state'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name
