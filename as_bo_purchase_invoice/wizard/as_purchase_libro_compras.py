# -*- coding: utf-8 -*-
from odoo import api, fields, models
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.tools.translate import _
from io import BytesIO, StringIO
import base64
import locale
from odoo import netsvc
from odoo import tools
from time import mktime
import logging

_logger = logging.getLogger(__name__)

# Declaracion del Wizard
class as_libro_compras(models.TransientModel):
    _name="as.libro.compras"
    _description = "Libro de compras"

    MESES = [
        ('1' , 'ENERO'),
        ('2' , 'FEBRERO'),
        ('3' , 'MARZO'),
        ('4' , 'ABRIL'),
        ('5' , 'MAYO'),
        ('6' , 'JUNIO'),
        ('7' , 'JULIO'),
        ('8' , 'AGOSTO'),
        ('9' , 'SEPTIEMBRE'),
        ('10' , 'OCTUBRE'),
        ('11' , 'NOVIEMBRE'),
        ('12' , 'DICIEMBRE'),
    ]

    anio_reporte = fields.Selection([(str(num), str(num)) for num in range(2020, (datetime.now().year)+8 )], 'Año', required=True, default=str(datetime.now().year))
    mes_reporte = fields.Selection(MESES, 'Mes', required=True, default=str(datetime.now().month))
    as_almacen = fields.Many2many('stock.location', string="Ubicacion destino", domain="[('usage', '=', 'internal')]")

    # @api.multi
    def imprimir_libro_compras_pdf(self):
        self.ensure_one()
        context = self._context
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('as_bo_purchase_invoice.as_purchase_summary_report_pdf').report_action(self, data=data)

    # @api.multi
    def imprimir_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.libro.compras'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_purchase_invoice.libro_compras_xlsx').report_action(self, data=datas)
    
    # @api.multi
    def libro_compras_txt(self):
        filename = 'libro_compras.txt'
        fila_facilito = ""
        # start_date = str(self.start_date)
        # end_date = str(self.end_date)
        anio_reporte = int(self.anio_reporte)
        mes_reporte = int(self.mes_reporte)
        if self.as_almacen:
            as_almacen = [self.as_almacen.ids]
        else:
            as_almacen = []

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
        saltopagina = "\n"
        numeracion =0
        for datos in self.env['account.move'].browse(resultado_query):
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
                    total_bruto = round((monto/0.13)+as_impuesto_especifico,2)
                else:
                    total_bruto = round(datos.amount_total,2) + round(as_descuento_total or 0,2)
                # total_bruto = obtener_a_bolivianos(total_bruto,datos.date_invoice)
                # fila_facilito += '3'+'|'+str(filas)+'|'+fecha+'|'+str(invoice.invoice_number)+'|'+str(invoice.qr_code_id.numero_autorizacion)+'|'+str(estado_factura[invoice.order_status])+'|'+str(ci_nit)+'|'+str(razon_social)+'|'+str(total_bruto)+'|0.00|0.00|0.00|'+str(total_bruto)+'|'+str(descuento)+'|'+str(total_debito)+'|'+str(total_iva)+'|'+str(invoice.control_code)+saltopagina

                fila_facilito +=str(1)+'|'+ str(numeracion)+'|'+ (datetime.strptime(str(datos.date_invoice),'%Y-%m-%d')).strftime('%d/%m/%Y')+'|'+ str(datos.as_nit)+'|'+str(datos.as_razon_social)+'|'+str(datos.as_numero_factura_compra)+'|'+ str(datos.as_numero_dui) +'|'+ str(datos.as_numero_autorizacion_compra)+'|'+ str(total_bruto)# IMPORTE TOTAL DE LA COMPRA
                totales_tasa_cero=0.00
                totales_tasa_cero+=total_bruto
                if compra.as_costo_cero == True:
                    fila_facilito+='|'+str(round(total_bruto,2)) # TASA EN CERO
                    tasacero += total_bruto
                else:
                    fila_facilito += '|'+str(round(as_impuesto_especifico,2)) # IMPORTE NO SUJETO A  CREDITO FISCAL
                    # fila_facilito+='|'+str(round(0.0,2)) # TASA EN CERO
                fila_facilito+='|'+str(round(total_bruto - as_impuesto_especifico - tasacero,2)) # DESCUENTOS, BONIFICACIONES Y REBAJAS OBTENIDAS
                fila_facilito+= '|'+str(round(as_descuento_total,2)) # SUBTOTAL
                subtotal = round(total_bruto - as_impuesto_especifico - as_descuento_total - tasacero,2)
                fila_facilito+= '|'+str(round(subtotal,2)) # IMPORTE BASE PARA CREDITO FISCAL BASE PARA CREDITO FISCAL
                if compra.as_iva == True:
                    credito_fiscal2 = round(subtotal*0.13,2)
                    fila_facilito+= '|'+str(round(subtotal*0.13,2)) # CREDITO FISCAL
                elif compra.as_costo_cero == True:
                    credito_fiscal2 = 0.0
                    fila_facilito+= '|'+str(round(credito_fiscal2,2)) # CREDITO FISCAL
                else:
                    credito_fiscal2 = round(((round(total_bruto,2)- round(as_impuesto_especifico,2))-round(as_descuento_total,2))*0.13, 2) # esto aqui mejorar
                    fila_facilito+= '|'+str(round(credito_fiscal2,2)) # CREDITO FISCAL
                fila_facilito+= '|'+str(datos.as_codigo_control_compra or '0')+'|'+saltopagina # CODIGO DE 


        id_file = self.env['txt.extended'].create({'as_txt_file': base64.encodestring(bytes(fila_facilito, 'utf-8')), 'as_file_name': filename,'as_txt_file': base64.encodestring(bytes(fila_facilito, 'utf-8'))})
        return {
            'view_mode': 'form',
            'res_id': id_file.id,
            'res_model': 'txt.extended',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
