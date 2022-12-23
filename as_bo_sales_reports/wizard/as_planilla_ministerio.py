# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class Ahorasoft_planillaMinisterio(models.TransientModel):
    _name = "as.report.ministerio"

    ass_payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)
    ass_lugar_trabajo=fields.Many2one('as.hr.lugar.trabajo', string="Lugar de Trabajo",required=True)
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.ministerio'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sales_reports.as_hr_planilla_ministerio').report_action(self, data=datas)