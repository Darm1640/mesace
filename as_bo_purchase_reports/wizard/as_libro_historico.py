# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
# Declaracion del Wizard
class as_libro_historico(models.TransientModel):
    _name="as.libro.historico"
    start_date  = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date    = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_productos = fields.Many2many('product.product', string="Producto")    
    _description = "Libro de historia"
    
    def imprimir_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.libro.historico'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_purchase_reports.as_libro_historico').report_action(self, data=datas)
    