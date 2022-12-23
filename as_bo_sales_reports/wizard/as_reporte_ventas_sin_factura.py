# -*- coding: utf-8 -*-
##############################################################################
from dateutil import relativedelta
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
from time import mktime
from datetime import datetime
from odoo import api, fields, models

class as_ventas_sin_factura(models.TransientModel):
    _name="as.report.resumen.ventas.sn.factura"
    
    fecha_inicial = fields.Date('Desde la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    fecha_final = fields.Date('Hasta la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    nombre_cliente = fields.Many2many('res.partner', string='Cliente')

    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.resumen.ventas.sn.factura'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sales_reports.as_ventas_sn_factura_xlsx').report_action(self, data=datas)

    