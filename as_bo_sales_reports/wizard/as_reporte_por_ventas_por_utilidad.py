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

class AhorasoftVentasUtilidad(models.TransientModel):
    _name = "as.ventas.utilidad"
    _description = "Informe de Ventas y Utilidad AhoraSoft"

    start_date = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date   = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_almacen = fields.Many2many('stock.location', string="Almacen", domain="[('usage', '=', 'internal')]")
    as_productos = fields.Many2many('product.product', string="Productos")
    as_categ_levels = fields.Integer(string="Niveles de Agrupación", help=u"Debe ser un entero igual o mayor a 1", default=4)
    as_consolidado = fields.Boolean(string="Consolidado", default=False)
    #as_fuente esta funcionaid 
    as_fuente = fields.Selection([('po','Pos'),('so','Ventas'),('both','Ambos')], default='so',string='Fuente',required=True)

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.ventas.utilidad'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sales_reports.as_informe_utilidad_report').report_action(self, data=datas)