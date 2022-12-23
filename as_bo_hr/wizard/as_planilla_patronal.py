# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AhorasoftplanillaSueldos(models.TransientModel):
    _name = "as.patronal.report"
    _description = "Report payslip Report AhoraSoft"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)
    as_filtro_dep = fields.Boolean( string="Agrupar por Departamento (PDF)")
    as_name_afp = fields.Many2many('as.hr.employee.afp', string='Filtro tipo de AFP')

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.patronal.report'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_hr.as_hr_planilla_patronal_report').report_action(self, data=datas)

    # @api.multi
    # def export_pdf(self):
    #     self.ensure_one()
    #     context = self._context
    #     data = {'ids': self.env.context.get('active_ids', [])}
    #     res = self.read()
    #     res = res and res[0] or {}
    #     data.update({'form': res})
    #     return self.env.ref('as_bo_hr.as_planilla_sueldos_pdf').report_action(self, data=data)