# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models
from time import mktime
from datetime import date, datetime

from odoo.exceptions import UserError
import logging
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)
class as_assets_report_facturas_pagadas(models.TransientModel):
    _name="as.report.factura.pagadas.pendientes"
    start_date = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_cliente  = fields.Many2many('res.partner', string="Nombre Cliente")

    def imprimir_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.factura.pagadas.pendientes'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xlsx_export'):
            return self.env.ref('as_spectrocom_sales.reporte_facturas_paga_pendi').report_action(self, data=datas)
     