# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models
from time import mktime
from datetime import date, datetime

from odoo.exceptions import UserError
import logging
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)
class as_assets_report_excel(models.TransientModel):
    _name="as.assets.report.excel"
    start_date = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_producto = fields.Many2many('product.product', string="Producto")
    as_lote = fields.Many2many('stock.production.lot', string='Lote')
    
    def imprimir_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.assets.report.excel'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xlsx_export'):
            return self.env.ref('as_bo_assets.reporte_siat_xlsx').report_action(self, data=datas)
     