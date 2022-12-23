# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import base64
import logging
_logger = logging.getLogger(__name__)

class Ahorasoftplanillaprevision(models.TransientModel):
    _name = "as.planilla.prevision"
    _description = "Report payslip Report AhoraSoft"

    as_payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.planilla.prevision'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_hr.as_pago_prevision').report_action(self, data=datas)    
