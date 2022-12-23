# -*- coding: utf-8 -*-
from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime
import time
import calendar
from time import mktime
from dateutil.relativedelta import relativedelta

class ReportTax(models.AbstractModel):
    _name = 'report.as_bo_purchase_invoice.as_pdf_report_libro_compras'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'nombre_empresa' : self.env.user.company_id.name or '',
            'sucursal' : self.env.user.company_id.city or '',
            'direccion1' : self.env.user.company_id.street or '',
            'vat' : self.env.user.company_id.vat or '',
            'libro_compras_resultado_pdf': self.libro_compras_resultado_pdf(data),

        }

    def libro_compras_resultado_pdf(self,data):
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
            AND to_char(account_move.date_invoice,'YYYY-MM') = %s
            ORDER BY date_invoice''',([fecha]))
        resultado_query = [i[0] for i in self.env.cr.fetchall()]
        compras_report=[]
        total_egresos, numeracion, total_compra = 0,0,0
        total_ice, total_subtotal, total_descuentos, total_base_credito, total_credito_fiscal, descuento_especifico,total_tasacero = 0.0,0.0,0.0,0.0,0.0,0.0,0.0
        for datos in self.env['account.move'].browse(resultado_query):
            vals = {}
            vals[100]='line'
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
                        INNER JOIN account_move ai ON ai.invoice_origin = po.name
                    WHERE
                        ai.id = '"""+str(datos.id)+"""'
                        AND sp.location_dest_id in """+str(as_almacen).replace('[','(').replace(']',')')+"""
                """)
                movimiento_almacen = [x[0] for x in cr.fetchall()]
                if not movimiento_almacen:
                    imprimir = False
            detalle=False
            if imprimir:
                numeracion += 1
                totales_tasa_cero=0.00
                if compra.as_iva == True:
                    monto = round(datos.amount_total,2) + round(as_descuento_total or 0,2)
                    total_bruto = (monto/0.13)+as_impuesto_especifico
                else:
                    total_bruto = round(datos.amount_total,2) + round(as_descuento_total or 0,2)
                # total_bruto = obtener_a_bolivianos(total_bruto,datos.date_invoice)
                
                vals[0] = 1 # No
                vals[1] = numeracion # No
                vals[2]= (datetime.strptime(str(datos.date_invoice),'%Y-%m-%d')).strftime('%d/%m/%Y') # FECHA DE LA FACTURA O DUI
                vals[3]= datos.as_nit # NIT PROVEEDOR
                vals[4]= datos.as_razon_social # NOMBRE O RAZON SOCIAL
                vals[5]= datos.as_numero_factura_compra # No DE LA FACTURA
                vals[6]= datos.as_numero_dui or '0' # No DE DUI
                vals[7]= datos.as_numero_autorizacion_compra # No DE AUTORIZACION
                vals[8]= total_bruto # IMPORTE TOTAL DE LA COMPRA
                totales_tasa_cero=0.00
                totales_tasa_cero+=total_bruto
                if compra.as_costo_cero == True:
                    vals[9] = round(total_bruto,2) # TASA EN CERO
                    tasacero += total_bruto
                else:
                    vals[9]= round(as_impuesto_especifico,2) # IMPORTE NO SUJETO A  CREDITO FISCAL
                    # vals[10,round(0.0,2) # TASA EN CERO
                vals[10] =  round(total_bruto,2)- round(as_impuesto_especifico,2) - round(tasacero,2) # DESCUENTOS, BONIFICACIONES Y REBAJAS OBTENIDAS
                vals[11] =round(as_descuento_total,2) # SUBTOTAL
                subtotal = total_bruto - as_impuesto_especifico - as_descuento_total - tasacero
                vals[12] = round(subtotal,2) # IMPORTE BASE PARA CREDITO FISCAL BASE PARA CREDITO FISCAL
                if compra.as_iva == True:
                    credito_fiscal2 = (subtotal*0.13)
                    vals[13] = (subtotal*0.13) # CREDITO FISCAL
                elif compra.as_costo_cero == True:
                    credito_fiscal2 = 0.0
                    vals[13] = credito_fiscal2 # CREDITO FISCAL
                else:
                    credito_fiscal2 = round(((round(total_bruto,2)- round(as_impuesto_especifico,2))-round(as_descuento_total,2))*0.13, 2) # esto aqui mejorar
                    vals[13] = credito_fiscal2 # CREDITO FISCAL
                vals[14] = datos.as_codigo_control_compra or '0' # CODIGO DE CONTROL
                vals[15] = compra.name # TIPO DE COMPRA
                total_compra += total_bruto
                total_ice += round(as_impuesto_especifico,2)+tasacero
                total_subtotal += subtotal
                total_tasacero += tasacero
                total_descuentos += as_descuento_total
                total_base_credito += round(total_bruto,2)- round(as_impuesto_especifico,2) - round(tasacero,2)- round(as_descuento_total,2)
                total_credito_fiscal += credito_fiscal2 #amount_to(total - as_impuesto_especifico)-as_descuento_totaltal * 0.13
            
            compras_report.append(vals)    

        # filas +=1
        valst = {}
        valst[100]='total'
        valst[0] = 'TOTALES'
        valst[8]= total_compra
        valst[9]= (total_ice)
        # sheet.write(filas,10, (total_tasacero)
        valst[10] =  (total_subtotal)
        valst[11] =  total_descuentos
        valst[12] =  (total_base_credito)
        valst[13] =  total_credito_fiscal
        compras_report.append(valst)
        return compras_report



    def convertir_ddmmyyy (self, date):
        return datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m/%Y')  
        # return True
   