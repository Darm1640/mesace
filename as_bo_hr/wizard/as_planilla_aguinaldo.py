# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AhorasoftplanillaSueldos_v_dos(models.TransientModel):
    _name = "as.payslip.report.aguinaldo"
    _description = "Report payslip Report AhoraSoft"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)
    as_filtro_dep = fields.Boolean( string="Agrupar por Departamento")
    as_name_afp = fields.Many2many('as.hr.employee.afp', string='Filtro tipo de AFP')
    as_lugar_trabajo=fields.Many2one('as.hr.lugar.trabajo', string="Lugar de Trabajo",required=True)

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.payslip.report.aguinaldo'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_hr.as_hr_planilla_aguinaldo').report_action(self, data=datas)