# -*- coding: utf-8 -*-
##############################################################################

from datetime import datetime, timedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.exceptions import UserError
from odoo.tools.translate import _
import base64
from odoo import netsvc
from odoo import tools
from time import mktime
import logging
from datetime import datetime
from odoo import api, fields, models

class as_kardex_productos_wiz(models.TransientModel):
    _name="as.sales.emit.wiz"
    _description = "Warehouse Reports by AhoraSoft"
    
    start_date  = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date    = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_vendedor = fields.Many2many('res.users', string="Vendedores")
    as_cliente  = fields.Many2many('res.partner', string="Clientes")
    # as_almacen funciona
    as_almacen = fields.Many2many('stock.location', string='Almacenes')
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.sales.emit.wiz'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sales_reports.sales_sumary_report_xls').report_action(self, data=datas)

    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.sales.emit.wiz'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_sales_reports.as_reporte_resumen_de_ventas_pdf').report_action(self, data=datas)
    