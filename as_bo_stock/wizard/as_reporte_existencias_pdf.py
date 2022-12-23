# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models
# access_as_reporte_existencias,as_reporte_existencias,model_as_reporte_existencias,stock.group_stock_user,1,1,1,1
class as_salidas_inventario_wiz(models.TransientModel):
    _name="as.reporte.existencias"
    _description = "Warehouse Reports by AhoraSoft"
    
    start_date = fields.Date('Desde la Fecha', default=fields.Date.context_today)
    end_date = fields.Date('Hasta la Fecha', default=fields.Date.context_today)
    as_almacen = fields.Many2many('stock.location', string="Almacen")
    as_productos = fields.Many2many('product.product', string="Productos")

    def imprimir_salidas_inventario_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.reporte.existencias'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_stock.as_reporte_existencias_pdf').report_action(self, data=datas)
