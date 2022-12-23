# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AhorasoftplanillaMinisterio(models.TransientModel):
    _name = "as.payslip.report.ministerio"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)
    # as_filtro_dep = fields.Boolean( string="Agrupar por Departamento")
    # as_name_afp = fields.Many2many('as.hr.employee.afp', string='Filtro tipo de AFP')
    as_lugar_trabajo=fields.Many2one('as.hr.lugar.trabajo', string="Lugar de Trabajo",required=True)
# fecha_final = fields.Date('Hasta la Fecha', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.payslip.report.ministerio'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_hr.as_hr_planilla_ministerio').report_action(self, data=datas)