# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime

from time import mktime
import logging
from datetime import datetime, timedelta
from datetime import datetime
class StockQuantityHistory(models.TransientModel):
    _name = 'lista.activos.fijos'
    
    start_date = fields.Date('Desde la Fecha', default=fields.Date.context_today)
    end_date = fields.Date('Hasta la Fecha', default=fields.Date.context_today)
    as_serie_lote_filter = fields.Many2one('stock.production.lot', string="Serie / Lote")
    as_producto_filter = fields.Many2many('product.product', string="Producto")
    as_marca_filter = fields.Many2one('product.brand', string="Marca")
    as_categoria_filter = fields.Many2one('account.asset.category', string="Categoria")

    def export_xlsx(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'lista.activos.fijos'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xlsx_export'):
            return self.env.ref('as_bo_assets.report_list_activ_fijos_xlsx').report_action(self, data=datas)
        
    def imprimir_salidas_inventario_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'lista.activos.fijos'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_assets.as_reporte_lista_activos_fijos_pdf').report_action(self, data=datas)       