# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AhorasoftGeneralPlanilla(models.TransientModel):
    _name = "as.planilla.tributaria"
    _description = "Report payslip Report AhoraSoft"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)

    def export_xls(self):
        context = self._context
        datas = {'ids': self.env.context.get('active_ids', [])}
        datas['model'] = 'as.planilla.tributaria'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_hr.as_hr_planilla_tributaria_report').report_action(self, data=datas)


    def export_pdf(self):
        self.ensure_one()
        context = self._context
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('as_bo_hr.as_planilla_tributaria_pdf_doc').report_action(self, data=data)