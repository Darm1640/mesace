# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import time
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import base64
import locale
from odoo import netsvc
from odoo import tools
from time import mktime
import logging
from odoo import api, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class as_purchase_libro_compras_tax(models.AbstractModel):
    _name = 'report.as_bo_purchase_invoice.libro_compras_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        #filtros
        anio_reporte = int(data['form']['anio_reporte'])
        mes_reporte = int(data['form']['mes_reporte'])
        as_almacen = data['form']['as_almacen']
        fecha = str(anio_reporte) + '-' + (str(mes_reporte) if mes_reporte>9 else ('0'+str(mes_reporte)))
        cr= self.env.cr
        self.env.cr.execute('''
           SELECT
            account_move.id
            FROM account_move 
            inner join as_tipo_factura tf on tf.id=account_move.as_tipo_factura
            WHERE account_move.move_type='in_invoice' AND account_move.state != 'cancel' AND account_move.as_tipo_documento='Factura' 
            AND to_char(account_move.invoice_date,'YYYY-MM') = %s
            ORDER BY invoice_date''',([fecha]))
        resultado_query = [i[0] for i in self.env.cr.fetchall()]

        filename = 'Libro_Compras.xls'
        sheet = workbook.add_worksheet('Libro de Compras')

        titulo = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bold':True})
        titulo2 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True })

        info1 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True })
        info2 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True, 'num_format': '#,##0.00' })
        info3 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True, 'num_format': '#,##0.00'})
        info4 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True, 'num_format': '#,##0.00'})
        info4j = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True})

        detalle1 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True})
        detalle2 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True})
        columnas = workbook.add_format({'font_size': 7, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True})
        columnas1 = workbook.add_format({'font_size': 7, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True})
        columnas2 = workbook.add_format({'font_size': 7, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True})

        datos1 = workbook.add_format({'font_size': 7, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':False })
        datos2 = workbook.add_format({'font_size': 7, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':False })
        datos3 = workbook.add_format({'font_size': 7, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':False, 'num_format': '#,##0.00'})
        datos4 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':False})
        datos3_entero = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':False})


        totales_sin_margenes = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': False, 'bottom': False, 'top': False, 'bold':True, 'num_format': '#,##0.00'})
        totales = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00'})
        

        sheet.set_column(1, 2, 15)
        sheet.set_column(3, 6, 10)
        sheet.set_column(7, 11, 15)
        sheet.set_column(12, 17, 15)
        filas = 5
        acumulativo_total_factura = 0.00
        acumulativo_total_ice = 0.00
        acumulativo_importe_excento = 0.00
        acumulativo_total_descuento = 0.00
        acumulativo_importe_neto = 0.00
        acumulativo_debito_fiscal = 0.00
        acumulativo_base_debito_fiscal = 0.00
        sheet.merge_range('A1:O1', 'LIBRO DE COMPRAS', titulo)
        sheet.set_row(0, 40)
        sheet.merge_range('A2:B2','Periodo', info2)
        sheet.merge_range('A3:B3','Año:', info3)
        sheet.merge_range('C3:D3',anio_reporte, info4j)
        sheet.merge_range('A4:B4','Mes:', info3)
        sheet.merge_range('C4:D4',mes_reporte, info4j)
        sheet.merge_range('J3:K3','Destino:', info3)
        if len(as_almacen) == 1:
            for almacen_obj in as_almacen:
                almacen=self.env['stock.location'].search([('id','=',almacen_obj)])
                sheet.merge_range('L3:O3', almacen.name, info3)
        else:
            sheet.merge_range('L3:O3', 'VARIOS', info3)
        sheet.merge_range('A5:B5','Nombre o Razon Social:', info3)
        sheet.merge_range('C5:D5',self.env.user.company_id.company_registry or "S/R", info3)
        sheet.merge_range('A6:B6','NIT:', info3)
        sheet.merge_range('C6:D6',self.env.user.company_id.vat or 'S/N', info3)
        sheet.set_row(6, 30)
        # sheet.write(6,0, 'ESPECIFICACION', columnas1)
        # sheet.write(6,0, 'No', columnas1)
        # sheet.write(6,1, 'FECHA DE LA FACTURA O DUI', columnas1)
        # sheet.write(6,2, 'NIT PROVEEDOR', columnas1)
        # sheet.write(6,3, 'NOMBRE O RAZON SOCIAL', columnas1)
        # sheet.write(6,4, 'No DE LA FACTURA', columnas1)
        # sheet.write(6,5, 'No DE DUI', columnas1)
        # sheet.write(6,6, 'No DE AUTORIZACION', columnas1)
        # sheet.write(6,7, 'IMPORTE TOTAL DE LA COMPRA', columnas1)
        # sheet.write(6,8, 'IMPORTE NO SUJETO A  CREDITO FISCAL', columnas1)
        # # sheet.write(6,10, 'VENTAS GRAVADAS A TASA CERO', columnas1)
        # sheet.write(6,9, 'SUBTOTAL', columnas1)
        # sheet.write(6,10, 'DESCUENTOS, BONIFICACIONES Y REBAJAS OBTENIDAS', columnas1)
        # sheet.write(6,11, 'IMPORTE BASE PARA CREDITO FISCAL', columnas1)
        # sheet.write(6,12, 'CREDITO FISCAL', columnas1)
        # sheet.write(6,13, 'CODIGO DE CONTROL', columnas1)
        # sheet.write(6,14, 'TIPO DE FACTURA', columnas1)

        sheet.write(6,0, 'Nº', columnas1)
        sheet.write(6,1, 'ESPECIFICACION', columnas1)
        sheet.write(6,2, 'NIT PROVEEDOR', columnas1)
        sheet.write(6,3, 'RAZON SOCIAL PROVEEDOR', columnas1)
        sheet.write(6,4, 'CODIGO DE AUTORIZACION', columnas1)
        sheet.write(6,5, 'NUMERO FACTURA', columnas1)
        sheet.write(6,6, 'NUMERO DUI/DIM', columnas1)
        sheet.write(6,7, 'FECHA DE FACTURA/DUI/DIM', columnas1)
        sheet.write(6,8, 'IMPORTE TOTAL COMPRA', columnas1)
        sheet.write(6,9, 'IMPORTE ICE', columnas1)
        sheet.write(6,10, 'IMPORTE IEHD', columnas1)
        sheet.write(6,11, 'IMPORTE IPJ', columnas1)
        sheet.write(6,12, 'TASAS', columnas1)
        sheet.write(6,13, 'OTRO NO SUJETO A CREDITO FISCAL', columnas1)
        sheet.write(6,14, 'IMPORTES EXENTOS', columnas1)
        sheet.write(6,15, 'IMPORTE COMPRAS GRAVADAS A TASA CERO', columnas1)
        # sheet.write(6,10, 'VENTAS GRAVADAS A TASA CERO', columnas1)
        sheet.write(6,16, 'SUBTOTAL', columnas1)
        sheet.write(6,17, 'DESCUENTOS/BONIFICACIONES /REBAJAS SUJETAS AL IVA', columnas1)
        sheet.write(6,18, 'IMPORTE GIFT CARD', columnas1)
        sheet.write(6,19, 'IMPORTE BASE CF', columnas1)
        sheet.write(6,20, 'CREDITO FISCAL', columnas1)
        sheet.write(6,21, 'TIPO COMPRA', columnas1)
        sheet.write(6,22, 'CODIGO DE CONTROL', columnas1)



        # sheet.write(7,0, '', columnas)
        # sheet.write(7,0, '', columnas)
        # sheet.write(7,1, '', columnas)
        # sheet.write(7,2, '', columnas)
        # sheet.write(7,3, '', columnas)
        # sheet.write(7,4, '', columnas)
        # sheet.write(7,5, '', columnas)
        # sheet.write(7,6, '', columnas)
        # sheet.write(7,7, 'A', columnas)
        # sheet.write(7,8, 'B', columnas)
        # # sheet.write(79,10, '', columnas)
        # sheet.write(7,9, 'C = A - B', columnas)
        # sheet.write(7,10, 'D', columnas)
        # sheet.write(7,11, 'E = C - D', columnas)
        # sheet.write(7,12, 'F = E*13%', columnas)
        # sheet.write(7,13, '', columnas)
        # sheet.write(7,14, '', columnas)

        sheet.write(7,0, '', columnas)
        sheet.write(7,1, '', columnas)
        sheet.write(7,2, '', columnas)
        sheet.write(7,3, '', columnas)
        sheet.write(7,4, '', columnas)
        sheet.write(7,5, '', columnas)
        sheet.write(7,6, '', columnas)
        sheet.write(7,7, '', columnas)
        sheet.write(7,8, 'A', columnas)
        sheet.write(7,9, 'X', columnas)
        sheet.write(7,10, 'T', columnas)
        sheet.write(7,11, 'Z', columnas)
        sheet.write(7,12, 'Y', columnas)
        # sheet.write(79,10, '', columnas)
        sheet.write(7,13, 'B', columnas)
        sheet.write(7,14, 'R', columnas)
        sheet.write(7,15, 'S', columnas)
        sheet.write(7,16, 'C = A - B-X-T-Z-Y-R-S', columnas)
        sheet.write(7,17, 'D', columnas)
        sheet.write(7,18, 'M', columnas)
        sheet.write(7,19, 'E = C - D-M', columnas)
        sheet.write(7,20, 'F = E*13%', columnas)
        sheet.write(7,21, '1', columnas)

        filas = 7
        total_egresos, numeracion, total_compra = 0,0,0
        total_ice, total_subtotal, total_descuentos, total_base_credito, total_credito_fiscal, descuento_especifico,total_tasacero,total_no_fiscal = 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0
        subtotal_nuevo_acum = 0.0
        for datos in self.env['account.move'].browse(resultado_query):
            for productos in datos.invoice_line_ids:
                # if productos.product_id.as_gift_card == False:
                #     gift_card_aux = 0.0
                #     continue
                # else:
                    # gift_card_aux = datos.as_gift_card
                    # continue
                gift_card_aux = 0
                continue
            tasacero=0.00
            if datos.as_impuesto_especifico > 0:
                as_impuesto_especifico = datos.as_impuesto_especifico
            elif datos.as_monto_exento:
                as_impuesto_especifico = datos.as_monto_exento
            else:
                as_impuesto_especifico = 0.00
            compra=self.env['as.tipo.factura'].search([('id','=',datos.as_tipo_factura.id)],limit=1)
            #calculo del descuento
            as_descuento_total = datos._obtener_total_descuento(datos.id)
            imprimir = True
            if as_almacen:
                cr.execute("""
                    SELECT
                        sp.id
                    FROM
                        stock_picking sp
                        INNER JOIN purchase_order po ON po.name = sp.origin
                        INNER JOIN account_invoice ai ON ai.origin = po.name
                    WHERE
                        ai.id = '"""+str(datos.id)+"""'
                        AND sp.location_dest_id in """+str(as_almacen).replace('[','(').replace(']',')')+"""
                """)
                movimiento_almacen = [x[0] for x in cr.fetchall()]
                if not movimiento_almacen:
                    imprimir = False
            detalle=False
            if imprimir:
                filas += 1
                numeracion += 1
                totales_tasa_cero=0.00
                if compra.as_iva == True:
                    monto = round(datos.amount_total,2) + round(as_descuento_total or 0,2)
                    total_bruto = (monto/0.13)+as_impuesto_especifico
                else:
                    total_bruto = round(datos.amount_total,2) + round(as_descuento_total or 0,2)
                # total_bruto = obtener_a_bolivianos(total_bruto,datos.date_invoice)
                
                # sheet.write(filas,0, 1, datos2) # No
                sheet.write(filas,0, numeracion, datos2) # No
                sheet.write(filas,1, '1', datos2) # No
                sheet.write(filas,2, datos.as_nit, datos3_entero) # NIT PROVEEDOR
                sheet.write(filas,3, datos.as_razon_social, datos1) # NOMBRE O RAZON SOCIAL
                sheet.write(filas,4, datos.as_numero_autorizacion_compra, datos3_entero) # No DE AUTORIZACION
                sheet.write(filas,5, datos.as_numero_factura_compra, datos3_entero) # No DE LA FACTURA
                sheet.write(filas,6, datos.as_numero_dui or '0', datos1) # No DE DUI
                if datos.invoice_date != False:
                    sheet.write(filas,7, (datetime.strptime(str(datos.invoice_date),'%Y-%m-%d')).strftime('%d/%m/%Y'), datos2) # FECHA DE LA FACTURA O DUI
                
                if datos.currency_id == 2:
                    total_bruto = total_bruto * 6.96

                if datos.as_tipo_factura.name == 'IVA' or datos.as_tipo_factura.name == 'Combustible':
                    sheet.write(filas,8, total_bruto, datos3) # IMPORTE TOTAL DE LA COMPRA
                    sheet.write(filas,9, 0.0, datos3) # as_importe_ice
                    sheet.write(filas,10, 0.0, datos3) # IHED
                    sheet.write(filas,11, 0.0, datos3) # P
                    sheet.write(filas,12, 0.0, datos3) # TASAS
                else:
                    sheet.write(filas,8, total_bruto, datos3) # IMPORTE TOTAL DE LA COMPRA
                    sheet.write(filas,9, datos.as_importe_ic, datos3) # as_importe_ice
                    sheet.write(filas,10, datos.as_impuesto_especifico, datos3) # IHED
                    sheet.write(filas,11, datos.as_importe_ipj, datos3) # P
                    sheet.write(filas,12, datos.as_tasas, datos3) # TASAS

                totales_tasa_cero=0.00
                totales_tasa_cero+=total_bruto
                # acumulador otro no sujeto a credito fiscal
                acum_fiscal = 0
                if datos.as_tipo_factura.name == 'Tasa 0':
                    sheet.write(filas,13, round(as_impuesto_especifico,2), datos3) # IMPORTE NO SUJETO A  CREDITO FISCAL
                    acum_fiscal = round(as_impuesto_especifico,2)
                    # sheet.write(filas,10,round(0.0,2), datos3) # TASA EN CERO
                elif datos.as_tipo_factura.name == 'IVA' or datos.as_tipo_factura.name == 'Servicios Basicos':
                    sheet.write(filas,13,  0.0, datos3) # TASAS
                elif datos.as_tipo_factura.name == 'Combustible':
                    sheet.write(filas,13,  total_bruto*0.30, datos3) # TASAS
                    acum_fiscal = total_bruto*0.30
                # else:
                else:
                    sheet.write(filas,13,0.0, datos3) # TASA EN CERO
                    tasacero += total_bruto
                sheet.write(filas,14, datos.as_exentos, datos3) # exentos
                if datos.as_tipo_factura.name == 'IVA':
                    sheet.write(filas,15,  0.0, datos3) # TASAS
                elif datos.as_tipo_factura.name == 'Tasa 0':
                    sheet.write(filas,15, total_bruto, datos3) # TASAS
                else:
                    sheet.write(filas,15, 0.0, datos3) # TASAS
                subtotal_nuevo = total_bruto - as_impuesto_especifico - datos.as_importe_ic - datos.as_impuesto_especifico - datos.as_importe_ipj - datos.as_tasas - datos.as_exentos
                subtotal_nuevo_acum += subtotal_nuevo

                # sheet.write(filas,16,round(subtotal_nuevo,2), datos3) # SUBTOTAL
                # sheet.write(filas, 16, '=H'+str(filas+1)+'*F'+str(filas+1), datos3)
                sheet.write(filas, 16, '=I'+str(filas+1)+'-J'+str(filas+1)+'-K'+str(filas+1)+'-L'+str(filas+1)+'-M'+str(filas+1)+'-N'+str(filas+1)+'-O'+str(filas+1)+'-P'+str(filas+1), datos3)
                # sheet.write(filas,17,  round(total_bruto,2)- round(as_impuesto_especifico,2) - round(tasacero,2), datos3) # DESCUENTOS, BONIFICACIONES Y REBAJAS OBTENIDAS
                sheet.write(filas,17, as_descuento_total, datos3) # DESCUENTOS, BONIFICACIONES Y REBAJAS OBTENIDAS
                sheet.write(filas,18, gift_card_aux, datos3) # P
                
                # subtotal = total_bruto - as_impuesto_especifico - as_descuento_total - tasacero
                d = round(total_bruto,2)- round(as_impuesto_especifico,2) - round(tasacero,2)
                subtotal = subtotal_nuevo - as_descuento_total - gift_card_aux

                # sheet.write(filas,19, round(subtotal,2), datos3) # IMPORTE BASE PARA CREDITO FISCAL BASE PARA CREDITO FISCAL
                sheet.write(filas, 19, '=Q'+str(filas+1)+'-R'+str(filas+1)+'-S'+str(filas+1), datos3)
                if compra.as_iva == True:
                    credito_fiscal2 = (subtotal*0.13)
                    # sheet.write(filas,20, (subtotal*0.13), datos3) # CREDITO FISCAL
                    sheet.write(filas, 20, '=T'+str(filas+1)+'*0.13', datos3)

                elif compra.as_costo_cero == True:
                    credito_fiscal2 = 0.0
                    # sheet.write(filas,20, credito_fiscal2, datos3) # CREDITO FISCAL
                    sheet.write(filas, 20, '=T'+str(filas+1)+'*0.13', datos3)
                else:
                    # credito_fiscal2 = round(((round(total_bruto,2)- round(as_impuesto_especifico,2))-round(as_descuento_total,2))*0.13, 2) # esto aqui mejorar
                    credito_fiscal2 = (subtotal*0.13)
                    # sheet.write(filas,20, credito_fiscal2, datos3) # CREDITO FISCAL
                    sheet.write(filas, 20, '=T'+str(filas+1)+'*0.13', datos3)
                if datos.as_tipo_compra.name == False:
                    tipo = ''
                else:
                    tipo = datos.as_tipo_compra.as_valor_tipo_compra
                # sheet.write(filas,21, compra.name, datos3_entero) # TIPO DE COMPRA
                sheet.write(filas,21, tipo, datos3_entero) # TIPO DE COMPRA
                sheet.write(filas,22, datos.as_codigo_control_compra or '0', datos3) # CODIGO DE CONTROL
                total_compra += total_bruto
                total_ice += round(as_impuesto_especifico,2)+tasacero
                total_subtotal += subtotal
                # acumulador no fiscal
                total_no_fiscal += acum_fiscal
                total_tasacero += tasacero
                total_descuentos += as_descuento_total
                total_base_credito += round(total_bruto,2)- round(as_impuesto_especifico,2) - round(tasacero,2)- round(as_descuento_total,2)
                total_credito_fiscal += credito_fiscal2 #amount_to(total - as_impuesto_especifico)-as_descuento_totaltal * 0.13

        filas +=1
        filacol='A'+str(filas+1)+':'+'H'+str(filas+1)
        sheet.merge_range(filacol, 'TOTALES', columnas1)
        sheet.write(filas,8, total_compra, totales)
        sheet.write(filas,9, '', totales)
        sheet.write(filas,10, '', totales)
        sheet.write(filas,11, '', totales)
        sheet.write(filas,12, '', totales)
        sheet.write(filas,13, total_no_fiscal, totales)
        # sheet.write(filas,10, (total_tasacero), totales)
        sheet.write(filas,14, '', totales)
        sheet.write(filas,15, '', totales)
        sheet.write(filas,16, subtotal_nuevo_acum, totales)
        sheet.write(filas,17, '')
        sheet.write(filas,18, total_descuentos, totales)
        # sheet.write(filas,19, (total_base_credito), totales)
        sheet.write_formula(filas,19,('SUM(T9:T'+str(filas)+')'),totales) #VALORADO INGRESO
        sheet.write(filas,20, total_credito_fiscal, totales)