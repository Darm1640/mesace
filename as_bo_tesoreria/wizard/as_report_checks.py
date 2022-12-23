# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
# Declaracion del Wizard
class as_report_checks(models.TransientModel):
    """Se ha agregado modelo wizard para reprte de cheques"""
    _name="as.report.checks"
    _description = "Se ha agregado modelo wizard para reprte de cheques"

    start_date  = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date    = fields.Date(string="Fecha Final",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    
    def imprimir_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.checks'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_cl_account_treasury.as_report_checks').report_action(self, data=datas)
    