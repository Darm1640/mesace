# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
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
class As_report_Tesoreria(models.Model):
    _inherit = 'as.tesoreria'
    
    def _fecha_actual(self):
        fecha_actual = time.strftime('%d-%m-%Y %H:%M:%S')
        struct_time_convert = time.strptime(fecha_actual, '%d-%m-%Y %H:%M:%S')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        date_time_convert = date_time_convert - timedelta(hours = 4)
        fecha_actual = date_time_convert.strftime('%d-%m-%Y %H:%M:%S')
        return fecha_actual
    
    def lineas_tesoreria(self):     
        lista=[]
        vals = {}
        # Titulos, subtitulos, filtros y campos del reporte  
       
        lineas_caja_chica = self.env['as.caja.chica'].sudo().search([('as_tesoreria_id', '=', self.id)])
        cont=0
        valorsito=0
        vector_papa=0
        valor_total_egreso=0
        if lineas_caja_chica:
            for linea_caja in lineas_caja_chica:
                if linea_caja.state == 'confirm': 
                    if cont == 0:
                        vals = {
                                'fecha': str(linea_caja.date.day) + '/'+ str(linea_caja.date.month)+ '/'+str(linea_caja.date.year),
                                'documento' :linea_caja.as_tipo_documento,
                                'nota': linea_caja.as_nota,
                                'monto' :linea_caja.as_amount - linea_caja.as_descuento_tesoreria,
                                'vector_papa': self.as_saldo_inicial - linea_caja.as_amount
                                }
                        lista.append(vals)
                        
                        valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                        vector_papa = self.as_saldo_inicial - linea_caja.as_amount
                        
                    if cont == 1:
                        if linea_caja.state == 'confirm':
                            vals = {
                                'fecha': str(linea_caja.date.day) + '/'+ str(linea_caja.date.month)+ '/'+str(linea_caja.date.year),
                                'documento' :linea_caja.as_tipo_documento,
                                'nota': linea_caja.as_nota,
                                'monto' :linea_caja.as_amount - linea_caja.as_descuento_tesoreria,
                                'vector_papa': vector_papa - linea_caja.as_amount
                                }
                            lista.append(vals)
                            
                            valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                            valorsito = vector_papa - linea_caja.as_amount
                            
                    if cont > 1:
                        if linea_caja.state == 'confirm':
                            vals = {
                                'fecha': str(linea_caja.date.day) + '/'+ str(linea_caja.date.month)+ '/'+str(linea_caja.date.year),
                                'documento' :linea_caja.as_tipo_documento,
                                'nota': linea_caja.as_nota,
                                'monto' :linea_caja.as_amount - linea_caja.as_descuento_tesoreria,
                                'vector_papa':  valorsito - linea_caja.as_amount
                                }
                            lista.append(vals)
                            
                            valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                            valorsito = valorsito - linea_caja.as_amount
                            cont+=1
                            
                    else:
                        cont+=1
                    
            return lista
    
    def obtener_totales(self):     
        lista=[]
        vals = {}
        # Titulos, subtitulos, filtros y campos del reporte  
       
        lineas_caja_chica = self.env['as.caja.chica'].sudo().search([('as_tesoreria_id', '=', self.id)])
        cont=0
        valorsito=0
        vector_papa=0
        valor_total_egreso=0
        if lineas_caja_chica:
            for linea_caja in lineas_caja_chica:
                if linea_caja.state == 'confirm': 
                    if cont == 0:
                        valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                        vector_papa = self.as_saldo_inicial - linea_caja.as_amount
                    if cont == 1:
                        if linea_caja.state == 'confirm':
                            valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                            valorsito = vector_papa - linea_caja.as_amount
                    if cont > 1:
                        if linea_caja.state == 'confirm':
                            
                            valor_total_egreso+=linea_caja.as_amount - linea_caja.as_descuento_tesoreria
                            valorsito = valorsito - linea_caja.as_amount
                            cont+=1
                    else:
                        cont+=1
        return valor_total_egreso
        # sheet.merge_range('A'+str(fila_caja+2)+':C'+str(fila_caja+2), 'TOTAL', number_total)
        # sheet.write(fila_caja+1, 3,  lines.as_saldo_inicial  , number_total_right)
        # sheet.write(fila_caja+1, 4, valor_total_egreso  , number_total_right)
        # sheet.write(fila_caja+1, 5,  lines.as_saldo_inicial - valor_total_egreso , number_total_right)