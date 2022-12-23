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
    _name="as.product.detail.wiz"
    _description = "Warehouse Reports by AhoraSoft"
    
    star_date = fields.Date(string='Desde la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    end_date = fields.Date(string='Hasta la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    producto = fields.Many2one('product.product',string='Producto',)
    producto_categ = fields.Many2one('product.category', string='Categoria de Producto')
    asesor = fields.Many2one('res.users', string='Asesor')
    cliente = fields.Many2one('res.partner', string='Cliente')
    agrupar = fields.Selection([('Ninguno','Ninguno'),('Vendedor','Vendedor'),('producto','Productos')], string="Agrupado por", default="Ninguno")
    # as_fuente = fields.Selection([('po','Pos'),('so','Ventas'),('both','Ambos')], default='both',string='Fuente')

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.product.detail.wiz'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sales_reports.product_detail_report_xls').report_action(self, data=datas)
