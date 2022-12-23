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

class as_resumen_ventas_gestion(models.TransientModel):
    _name="as.report.resumen.cuentas.cobrar"
    
    fecha_inicial = fields.Date('Desde la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    fecha_final = fields.Date('Hasta la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    nombre_cliente = fields.Many2many('res.partner', string='Cliente', required=True)
    # as_tipo_producto=fields.Selection(selection=[('', 'Todos'),('consu','Consumible'),('product','Almacenable'),('service','Servicio')],default='product', string="Tipo de Producto", required=True)
    # as_almacen= fields.Many2many('stock.location', string="Almacen")
    # as_ciudad= fields.Many2many('res.country.state', string="Ciudad")
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.resumen.cuentas.cobrar'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sales_reports.as_resumen_cuentas_cobrar_xlsx').report_action(self, data=datas)

    