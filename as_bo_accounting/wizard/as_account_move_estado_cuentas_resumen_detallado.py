# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime

from time import mktime
import logging
from datetime import datetime, timedelta
from datetime import datetime
class ReporteCuentasDetallado(models.TransientModel):
    _name = 'as.resumen.cuentas.detallado'

    as_cuentas_proveedor = fields.Many2one('account.account', string='Cuenta', required = True)
    as_nombre_cliente= fields.Many2one('res.partner', string="Proveedor")
    start_date  = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date    = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.resumen.cuentas.detallado'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_accounting.as_resumen_estado_cuentas_xlsx').report_action(self, data=datas)
        
        