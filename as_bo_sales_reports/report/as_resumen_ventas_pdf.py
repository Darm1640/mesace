# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields,api,_
from datetime import datetime, timedelta
from time import mktime
import logging
import time
from io import BytesIO
from odoo.tools.translate import _
from odoo.tools.image import image_data_uri
import math
from odoo.exceptions import UserError
from urllib.request import urlopen
import locale
_logger = logging.getLogger(__name__)

class as_sales_emit_pdf(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.as_resumen_ventas_pdf'
    def _get_report_values(self, docids, data=None):
        
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
                'fecha_actual' : self._fecha_actual(),
                'fecha_inicial' : self._fecha_inicial(data['form']),
                'fecha_final' : self._fecha_final(data['form']),
                'lista_salidas_inventarios' : self.generate_xlsx_report2(data),
                'logo':self.env.user.company_id.logo,
                'usuario':self.env.user.partner_id.name,
                'filtro_almacen':self.filtro_almacen(data),
        }
    def generate_xlsx_report2(self,data):     
        
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['start_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        filas = 11 
        filtro_fechas_so = " AND (so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date BETWEEN '" + str(data['form']['start_date']) + "' AND '" + str(data['form']['end_date']) + "'"
        dict_vendedores = []
        lista=[]
        if data['form']['as_vendedor']:
            for ids in data['form']['as_vendedor']:
                dict_vendedores.append(ids)
        if dict_vendedores:
            filtro_vendedores_so = "AND so.user_id in "+str(dict_vendedores).replace('[','(').replace(']',')')
        else:
            filtro_vendedores_so = ''
        dict_clientes = []
        if data['form']['as_cliente']:
            for ids in data['form']['as_cliente']:
                dict_clientes.append(ids)
        if dict_clientes:
            filtro_clientes = "AND cliente.id in "+str(dict_clientes).replace('[','(').replace(']',')')
        else:
            filtro_clientes = ''
        dict_aux = []
        dict_almacen = []
        if data['form']['as_almacen']:
            for ids in data['form']['as_almacen']:
                dict_almacen.append(ids)
                dict_aux.append(ids)
        if dict_almacen:
            filtro_almacen = "WHERE sl.id in "+str(dict_almacen).replace('[','(').replace(']',')')
        else:
            filtro_almacen = ''
        
        filtro_almacenes_name = 'VARIOS'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        
        consulta_so = ("""
                SELECT
            sl.name as almacn,
            sl.id
            FROM stock_location AS sl
            """ + str(filtro_almacen) + """
            """)           
        self.env.cr.execute(consulta_so)
        k = [j for j in self.env.cr.fetchall()]
        
        for e in k: 
            listaventas=[]
            listatotales=[]
            consulta = ("""
                    SELECT
                to_char((so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date,'DD/MM/YYYY') AS fecha
                ,so.name as nro_pedido
                ,atp.name
                ,COALESCE(cliente.as_code, 'S/CODIGO')	as codigo_cliente
                ,COALESCE(cliente.name, 'S/NOMBRE')	AS nombre_cliente
                ,cliente.as_razon_social as razonkkkk
                ,so.amount_total as importe
                ,am.amount_total as facturado
                ,am.id as pago 
                ,am.amount_residual AS saldo
                ,CASE 
                    WHEN so.state = 'sale' THEN 'Pedido de venta'
                    WHEN so.state = 'done' THEN 'Realizado'
                    ELSE 'Devolucion'
                END as estado
                FROM sale_order AS so
                left JOIN res_users AS usuarios ON usuarios.id = so.user_id
                left join as_template_project atp ON atp.id=so.as_template_id
                left JOIN res_partner AS asesor ON asesor.id = usuarios.partner_id
                LEFT JOIN res_partner AS cliente ON cliente.id = so.partner_id
                left join account_move am on am.invoice_origin=so.name
                left join account_payment ap on ap.move_id=am.id
                left join account_move amove on amove.ref=am.name
                left join stock_picking sp on sp.origin=so.name
                left join stock_location sl on sp.location_id=sl.id
                WHERE so.state NOT IN ('cancel','draft')
                AND sl.id=""" + str(e[1]) + """
                """ + str(filtro_fechas_so) + """
                """ + str(filtro_vendedores_so) + """
                """ + str(filtro_clientes) + """
                ORDER BY so.name desc
                """)           
            self.env.cr.execute(consulta)
            ventas = [j for j in self.env.cr.fetchall()]
            vals = {}
            if ventas != []:
                vals = {
                'almacen': e[0],
                }
                importe=0.0
                facturado_total = 0.0
                pago_bs = 0.0
                saldo = 0.0
                # sheet.write(filas,0,e[0],number_right_bold)#fecha
                filas+=1
                for v in ventas:
                    importe+=v[6]
                    if v[7]==None:
                        facturado_total+=0.0
                    else:
                        facturado_total+=v[7]
                    # sheet.write(filas,0,v[0],number_right)#fecha
                    # sheet.write(filas,1,v[1],number_right)#pedido
                    # sheet.write(filas,2,v[2],number_right)#codigo
                    # sheet.write(filas,3,v[3],number_left)#code cliente
                    # sheet.write(filas,4,v[4],number_left)#cliente
                    # sheet.write(filas,5,v[5],number_left)#razon social
                    # sheet.write(filas,6,v[6],number_right)#importe
                    # sheet.write(filas,7,v[7],number_right)#facturado
                    id_invoice = self.env['account.move'].search([('id','=',v[8])])
                    diario=0.0
                    diario_str=''
                    if id_invoice:
                        for pagos in id_invoice.get_payment():
                            if pagos.currency_id.name == 'USD':
                                diario=round((pagos.amount/0.143678000000),1)
                                diario_str=str(diario)+'  '
                                pago_bs+=diario
                            else:
                                diario=pagos.amount
                                diario_str=str(diario)+'  '
                                pago_bs+=diario
                    if v[9]==None:
                        saldo+=0.0
                    else:
                        saldo+=v[9]
                    # sheet.write(filas,8,diario_str,number_right) # tipo de pago
                    # sheet.write(filas,9,v[9],number_right)#saldo
                    # sheet.write(filas,10,v[10],number_left)#estad
                    vals2={
                    'val0':v[0],
                    'val1':v[1],
                    'val2':v[2],
                    'val3':v[3],
                    'val4':v[4],
                    'val5':v[5],
                    'val6':v[6],
                    'val7':v[7],
                    'val8':diario_str,
                    'val9':v[9],
                    'val10':v[10],
                    }
                    listaventas.append(vals2)
                
                vals3={
                    'total_importe':importe,
                    'total_facturado_total':facturado_total,
                    'total_pago_bs':pago_bs,
                    'total_saldo':saldo,
                }
                listatotales.append(vals3)   
                vals['contenido']= listaventas
                vals['totales']= listatotales
                lista.append(vals)
        return lista
                    
    def _fecha_actual(self):
        fecha_actual = time.strftime('%d-%m-%Y %H:%M:%S')
        struct_time_convert = time.strptime(fecha_actual, '%d-%m-%Y %H:%M:%S')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        date_time_convert = date_time_convert - timedelta(hours = 4)
        fecha_actual = date_time_convert.strftime('%d-%m-%Y %H:%M:%S')
        return fecha_actual

    def _fecha_inicial(self,filtros):
        fecha_inicial = filtros['start_date']
        struct_time_convert = time.strptime(fecha_inicial, '%Y-%m-%d')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        fecha_inicial = date_time_convert.strftime('%d-%m-%Y')
        return fecha_inicial

    def _fecha_final(self,filtros):
        fecha_final = filtros['end_date']
        struct_time_convert = time.strptime(fecha_final, '%Y-%m-%d')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        fecha_final = date_time_convert.strftime('%d-%m-%Y')
        return fecha_final
    def filtro_almacen(self,filtros):
        dict_aux = []
        dict_almacen = []
        almacen=filtros['form']['as_almacen']
        if almacen:
            for ids in almacen:
                dict_almacen.append(ids)
                dict_aux.append(ids)
        if dict_almacen:
            filtro_almacen = "WHERE sl.id in "+str(dict_almacen).replace('[','(').replace(']',')')
        else:
            filtro_almacen = ''
        # sheet.write(8, 0, 'Almacen', titulo4)
        filtro_almacenes_name = 'VARIOS'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', ' + almacen_obj.name
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        # sheet.merge_range('B9:C9', filtro_almacenes_name,titulo3)
        return filtro_almacenes_name
    