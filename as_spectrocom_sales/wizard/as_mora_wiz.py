# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models
from time import mktime
from datetime import date, datetime

from odoo.exceptions import UserError
import logging
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)
class as_mora_report_excel(models.TransientModel):
    _name="as.report.mora.excel"
    start_date = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_cliente  = fields.Many2many('res.partner', string="Clientes")
    as_almacen = fields.Many2many('stock.location', string='Ubicacion')
    # as_negocio = fields.Many2many('as.business.unit', string='Unidad de negocio')

    def imprimir_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.mora.excel'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xlsx_export'):
            return self.env.ref('as_spectrocom_sales.reporte_mora_xlsx').report_action(self, data=datas)