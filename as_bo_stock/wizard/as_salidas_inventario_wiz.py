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
class as_salidas_inventario_wiz(models.TransientModel):
    _name="as.salidas.inventario.wiz"
    _description = 'Salidas de Inventario'

    
    ESTADOS = [
        ('draft', 'Borrador'),
        ('confirmed', 'Esperando Disponibilidad'),
        ('done', 'Realizado'),
    ]

    start_date = fields.Date('Desde la Fecha', default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    end_date = fields.Date('Hasta la Fecha', default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    estado_salidas  = fields.Selection(ESTADOS, 'Estado')
    product = fields.Many2one('product.product', 'Producto')
    location_m2m = fields.Many2many('stock.location', string='Ubicacion')
    location = fields.Many2one('stock.location', 'Ubicacion')

    def export_xlsx(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.salidas.inventario.wiz'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xlsx_export'):
            return self.env.ref('as_bo_stock.salidas_inventario_xlsx').report_action(self, data=datas)

    # def imprimir_salidas_inventario_pdf(self):
    #     context = self._context
    #     datas = {'ids': context.get('active_ids', [])}
    #     datas['model'] = 'as.salidas.inventario.wiz'
    #     datas['form'] = self.read()[0]
    #     for field in datas['form'].keys():
    #         if isinstance(datas['form'][field], tuple):
    #             datas['form'][field] = datas['form'][field][0]
    #     return self.env.ref('as_bo_stock.as_salidas_inventario_qweb').report_action(self, data=datas)

    