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

class as_repair_historial_pdf(models.AbstractModel):
    _name = 'report.as_spectrocom_repair.as_historial_reparaciones_pdf'
    _inherit = 'report.report_xlsx.abstract'
    
    def _get_report_values(self, docids, data=None):
        
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
                'fecha_actual' : self._fecha_actual(),
                'fecha_inicial' : self._fecha_inicial(data['form']),
                'fecha_final' : self._fecha_final(data['form']),
                'lista_salidas_inventarios' : self.generate_xlsx_report(data),
                'logo':self.env.user.company_id.logo,
                'usuario':self.env.user.partner_id.name,
                'estado':self.estado(data['form']),
                'series':self.function_series(data['form']),
                }

    def generate_xlsx_report(self,data):     
        # Preparando variables para cada casod e consulta
        #consultas
        dict_productos=[]
        if data['form']['as_estado']:
            filtro_estado = """AND ro.state = '"""+str(data['form']['as_estado'])+"""'"""
        else:
            filtro_estado = ''
        if data['form']['as_series']:
            valor = data['form']['as_series']
            # for line in data['form']['as_series']:
            #     dict_productos.append(line)
            filtro_cliente ="""AND spl.id = '"""+str(data['form']['as_series'])+"""'"""
        else:
            filtro_cliente = ''
        # if dict_productos:
        #     filtro_cliente = "AND spl.name = "+str(dict_productos).replace('[','(').replace(']',')')
        lista=[]
        consulta_product= ("""
        select 
            ro.name as "item",
            to_char((( ro.fecha_confirmar AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) AS "fecha_ingreso",
            rp.name as "cliente",
            pt.name as "producto",
            ro.id,
            spl.name as "lote",
            ro.internal_notes as "diagnostico",
            ro.quotation_notes as "reparacion",
            to_char((( ro.fecha_finalizar AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) AS "fecha_salida"
            ,CASE 
            WHEN ro.state = 'done' THEN 'Reparado'
            WHEN ro.state = 'confirmed' THEN 'Confirmado'
            WHEN ro.state = 'draft' THEN 'Cotizacion'
            WHEN ro.state = 'under_repair' THEN 'En reparacion'
            WHEN ro.state = 'ready' THEN 'Listo para reparar'
            WHEN ro.state = '2binvoiced' THEN 'Para ser facturado'
            WHEN ro.state = 'invoice_except' THEN 'Excepcion de factura'
            WHEN ro.state = 'cancel' THEN 'Cancelado'
            END as estado
            from repair_order ro
            left join res_partner rp on rp.id=ro.partner_id
            left join product_product pp on pp.id=ro.product_id
            left join product_template pt on pt.id=pp.product_tmpl_id
            left join repair_line rl on rl.id=ro.id
            left join stock_production_lot spl on spl.id=ro.lot_id
            left join stock_picking sp on  sp.origin=ro.name
            WHERE
                (ro.create_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '"""+str(data['form']['start_date'])+"""'
                AND (ro.create_date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '"""+str(data['form']['end_date'])+"""' """+str(filtro_estado)+""" """+str(filtro_cliente)+"""
        """)
        self.env.cr.execute(consulta_product)
        productos = [k for k in self.env.cr.fetchall()]
        if productos != []:
            for produ in productos:
                cons=("""select rt.name from repair_order_repair_tags_rel rortl join repair_tags rt on rortl.     repair_tags_id=rt.id
                    WHERE rortl.repair_order_id="""+str(produ[4])+""" """)
                self.env.cr.execute(cons)
                categoria = [k for k in self.env.cr.fetchall()]
                categoriprodu=''
                for linea in categoria:
                    categoriprodu+=linea[0]+''
                    
                vals={
                    'val1':produ[0],
                    'val2':produ[1],
                    'val3':produ[2],
                    'val4':produ[3],
                    'val5':categoriprodu,
                    'val6':produ[5],
                    'val7':produ[6],
                    'val8':produ[7],
                    'val9':produ[8],
                    'val10':produ[9],
                }
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
    def estado(self, data):
        filtro=''
        if data['as_estado']:
            if data['as_estado']== 'done':
                filtro='Reparado'
            if data['as_estado']== 'confirmed':
                filtro='Confirmado'
            if data['as_estado']== 'draft':
                filtro='Cotizacion'
            if data['as_estado']== 'under_repair':
                filtro='En reparacion'
            if data['as_estado']== 'ready':
                filtro='Listo para reparar'
            if data['as_estado']== '2binvoiced':
                filtro='Para ser facturado'
            if data['as_estado']== 'invoice_except':
                filtro='Excepcion de factura'
            if data['as_estado']== 'cancel':
                filtro='Cancelado'
        else:
            filtro='Todos los estados'
        return filtro
    def function_series(self,data):
        # dict_aux = []
        # dict_almacen = []
        # almacen=data['as_series']
        # if almacen:
        #     for ids in almacen:
        #         dict_almacen.append(ids)
        #         dict_aux.append(ids)
        # filtro_almacenes_name = 'Todos'
        # for y in dict_aux:
        #     almacen_obj = self.env['stock.production.lot'].search([('id', '=', y)], limit=1)
        #     filtro_almacenes_name += ', ' + almacen_obj.name 
        # if len(dict_aux) == 1:
        #     filtro_almacenes_name = self.env['stock.production.lot'].search([('id', '=', dict_aux[0])], limit=1).name
        # return filtro_almacenes_name
        pass