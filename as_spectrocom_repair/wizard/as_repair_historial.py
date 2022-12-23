# -*- coding: utf-8 -*-

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

_logger = logging.getLogger(__name__)


# Declaracion del Wizard
class as_historial_reparaciones(models.TransientModel):
    _name="as.historial.reparaciones"
    _description = 'historial reparaciones'

    start_date  = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date    = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_estado = fields.Selection(
        [
            ('', 'Todos'),
            ("draft", "Cotizacion"),
            ("under_repair", "En reparacion"),
            ("cancel", "Cancelado"),
            ("done", "Reparado"),
            ("confirmed", "Confirmado"),
        ],string="Estado" )
    
    
    def export_xlsx(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.historial.reparaciones'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xlsx_export'):
            return self.env.ref('as_spectrocom_repair.as_historial_reparaciones_xlsx').report_action(self, data=datas)
        
    def imprimir_salidas_inventario_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.historial.reparaciones'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_spectrocom_repair.as_reporte_existencias_pdf').report_action(self, data=datas)
    
    def _rutas_dominio(self):
        domain = {
            'domain': {
                'as_series':[],
                }
        }
        self.env.cr.execute("""
            select spl.id
            from repair_order as  ro
            join stock_production_lot as spl on spl.id = ro.lot_id
        """)
        #182 registros
        tamaño_ids=[]
        for y in self.env.cr.fetchall():
            tamaño_ids.append(y[0])
        domain = {
            'domain':	{
                'as_series': [('id','in',tuple(tamaño_ids))]
            }
        }
        return [('id','in',tuple(tamaño_ids))]
    
    as_series=fields.Many2one('stock.production.lot',string="Nro serie")
    # as_series=fields.Char(string="Nro serie")