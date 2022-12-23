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
    _name = 'report.as_bo_assets.as_report_list_activos_fijos_pdf'
    _inherit = 'report.report_xlsx.abstract'
    
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
                'fecha_actual' : self._fecha_actual(),
                'lista_salidas_inventarios' : self.generate_xlsx_report(data),
                'logo':self.env.user.company_id.logo,
                'usuario':self.env.user.partner_id.name,
                'series':self.obtneer_serie(data['form']),
                'producto':self.obtneer_productos(data['form']),
                }

    def generate_xlsx_report(self,data):     
        # Preparando variables para cada casod e consulta
        #consultas
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
        lista=[]
        consulta_product= ("""
        select
            pp.default_code, 
            ass.as_code_assets,
            pt.name,
            spl.name,
            pb.name,
            pm.name,
            pt.product_part_num,
            aac.name
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
        """)
        self.env.cr.execute(consulta_product)
        productos = [k for k in self.env.cr.fetchall()]
        cont=0
        if productos != []:
            for linea in productos:
                vals={
                    'contador':cont,
                    'val0':linea[0],
                    'val1':linea[1],
                    'val2':linea[2],
                    'val3':linea[3],
                    'val4':linea[4],
                    'val5':linea[5],
                    'val6':linea[6],
                    'val7':linea[7],
                }
                cont+=1
                lista.append(vals)        
        return lista
    
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

        return nombre_del_producto
    
    
    def obtneer_serie(self,data):
        almacen=data['as_serie_lote_filter']
        nombre_del_producto='Todos'
        if almacen:
            id_producto = self.env['stock.production.lot'].search([('id', '=',almacen)], limit=1)
            nombre_del_producto += ', ' + id_producto.name 
        else:
            nombre_del_producto += ' '
        return nombre_del_producto
    
    
    def _fecha_actual(self):
        fecha_actual = time.strftime('%d-%m-%Y %H:%M:%S')
        struct_time_convert = time.strptime(fecha_actual, '%d-%m-%Y %H:%M:%S')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        date_time_convert = date_time_convert - timedelta(hours = 4)
        fecha_actual = date_time_convert.strftime('%d-%m-%Y %H:%M:%S')
        return fecha_actual
    