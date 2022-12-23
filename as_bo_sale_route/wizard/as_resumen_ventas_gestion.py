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
    _name="as.report.resumen.ventas.gestion"
    
    fecha_inicial = fields.Selection([(str(num), str(num)) for num in range(2020, (datetime.now().year)+4 )], 'Gestion Inicial', required=True, default=str(datetime.now().year))
    nombre_cliente = fields.Many2many('res.partner', string='Cliente')
    # as_tipo_producto=fields.Selection(selection=[('', 'Todos'),('consu','Consumible'),('product','Almacenable'),('service','Servicio')],default='product', string="Tipo de Producto", required=True)
    as_almacen= fields.Many2many('stock.location', string="Almacen")
    # as_divisas=fields.Selection(selection=[('62','BOB'),('2','USD')],default='62', string="Divisa", required=True)
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.resumen.ventas.gestion'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sale_route.as_resumen_ventas_gestion_xlsx').report_action(self, data=datas)

    