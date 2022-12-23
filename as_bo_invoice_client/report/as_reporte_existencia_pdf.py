# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models
import time
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
from odoo.tools.translate import _
import base64
import io
import locale
from odoo import netsvc
from odoo import tools
from odoo.exceptions import UserError
from time import mktime
import logging
from odoo.tools.misc import formatLang

class ReportTax(models.AbstractModel):
    _name = 'report.as_bo_stock.as_pdf_reporte_existencias'
    def _get_report_values(self, docids, data=None):
        
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
                'logo':self.env.user.company_id.logo,
                'usuario':self.env.user.partner_id.name,
                'nit' : self.env.user.company_id.vat or '',
                'direccion1' : self.env.user.company_id.street or '',
                'telefono' : self.env.user.company_id.phone or '',
                'fecha_actual' : self._fecha_actual(),
                'fecha_inicial' : self._fecha_inicial(data['form']),
                'fecha_final' : self._fecha_final(data['form']),
                'lista_salidas_inventarios' : self.generate_xlsx_report2(data),
                'nombre_almacen':self.nombre_almacen(data['form']),
                # 'nombre_productos': self.nombre_productos(data['form']),
                }

    def generate_xlsx_report2(self,data):
        dict_aux = []
        
        dict_almacen = []
        if data['form']['as_almacen']:
            for line in data['form']['as_almacen']:
                dict_almacen.append('('+str(line)+')')
                dict_aux.append(line)
        else:
            almacenes_internos = self.env['stock.location'].search([('usage', '=', 'internal')])
            for line in almacenes_internos:
                dict_almacen.append('('+str(line.id)+')')
                dict_aux.append(line.id)
        
        dict_productos = []
        if data['form']['as_productos']:
            for line in data['form']['as_productos']:
                dict_productos.append(line)
        if dict_productos:
            filtro_productos = "AND sm.product_id in "+str(dict_productos).replace('[','(').replace(']',')')
        else:
            filtro_productos = ''
        vals={}
        lista=[]
        lista_auxiliar=[]
        lista_datos=[]
        for almacen in dict_almacen:
            listaventas=[]
            id_almacen = int(str(almacen).replace('(','').replace(')',''))
            almacen_obj = self.env['stock.location'].search([('id', '=', id_almacen)], limit=1)
            nombre_almacen=almacen_obj.name
            vals={
            'nombre_almacen':nombre_almacen,
            }
            order_by = ' ORDER BY 3'
            order_by += ' , 2'
            query_ids = ("""
                SELECT
                    pp.id as "ID",
                    pp.default_code as codigo_producto,
                    pt.name as "Codigo Producto",
                    pu.name
                FROM
                    product_product pp
                    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    INNER JOIN uom_uom pu ON pu.id = pt.uom_id
                WHERE
                    pp.id in
                    (SELECT
                        sm.product_id
                    FROM
                        stock_move sm
                        LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
                        LEFT JOIN stock_inventory si ON si.id = sm.inventory_id
                    WHERE
                        sm.state = 'done'
                        AND (sm.location_id IN """+str(almacen)+"""
                        OR sm.location_dest_id IN """+str(almacen)+""")
                        
                        AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(data['form']['end_date'])+"""'
                        """+filtro_productos+"""
                    GROUP BY 1)
                """+order_by+"""
                """)
            self.env.cr.execute(query_ids)
            product_categories = [l for l in self.env.cr.fetchall()]
            #product_categories contiene el codigo el nombre y la unidad de
            for producto in product_categories:   
                vals2={
                    'val1':producto[1],
                    'val2':producto[2],
                    'val3':producto[3],
                }
                query_movements = ("""
                    SELECT
                        pp.default_code as "Codigo Producto"
                        ,CONCAT(COALESCE(sp.name, sm.name), ' - ', COALESCE(sp.origin, 'S/Origen')) as "Comprobante"
                        ,COALESCE((sp.date_done AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date, sm.date::date) as "Fecha"
                        ,COALESCE(rp.name,'SIN NOMBRE') as "Cliente/Proveedor"
                        ,CASE
                        WHEN (sm.location_dest_id IN """+str(almacen)+""" AND sm.location_id NOT IN """+str(almacen)+""") THEN sm.product_qty
                        WHEN (sm.location_id IN """+str(almacen)+""" AND sm.location_dest_id NOT IN """+str(almacen)+""") THEN -sm.product_qty
                        ELSE 0 END as "Cantidad"
                    ,COALESCE(sm.price_unit, 0) as "Costo"
                        FROM
                            stock_move sm
                            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                            LEFT JOIN product_product pp ON pp.id = sm.product_id
                            LEFT JOIN res_partner rp ON rp.id = sp.partner_id
                        WHERE
                            sm.state = 'done'
                            AND (sm.location_id IN """+str(almacen)+""" or sm.location_dest_id IN """+str(almacen)+""")
                            AND pp.id = """+str(producto[0])+"""
                            AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(data['form']['end_date'])+"""'
                        ORDER BY COALESCE(sp.date_done, sm.date)  asc
                    """)
                self.env.cr.execute(query_movements)
                lineas = [j for j in self.env.cr.fetchall()]
                cantidad=0.0
                valorado=0.0
                total_valorado=0.0
                for k in lineas:
                    cantidad+=k[4]
                    valorado+=k[4]*k[5]
                    vals2['cantidad']=cantidad
                    vals2['valorado']=valorado
                if cantidad == 0.0:
                    total_valorado+=0
                else:
                    total_valorado+=valorado/cantidad
                vals2['precio_costo']=total_valorado
                listaventas.append(vals2)
            #si encontramos movimientos pasamos a la impresion
            
            vals['contenido']= listaventas
            lista.append(vals)
        return lista
   

    def nombre_almacen(self, data):
        dict_aux = []
        dict_almacen = []
        if data['as_almacen']:
            for line in data['as_almacen']:
                dict_almacen.append('('+str(line)+')')
                dict_aux.append(line)
        else:
            almacenes_internos = self.env['stock.location'].search([('usage', '=', 'internal')])
            for line in almacenes_internos:
                dict_almacen.append('('+str(line.id)+')')
                dict_aux.append(line.id)
        filtro_almacenes_name = 'Varios'
        for y in dict_aux:
            almacen_obj = self.env['stock.location'].search([('id', '=', y)], limit=1)
            filtro_almacenes_name += ', '+almacen_obj.name
        if len(dict_aux)==1 :
            filtro_almacenes_name = self.env['stock.location'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name
    
    
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
