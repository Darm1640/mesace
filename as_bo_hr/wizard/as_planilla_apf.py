# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AhorasoftGeneralPlanilla(models.TransientModel):
    _name = "as.planilla.afp"
    _description = "Report payslip Report AhoraSoft"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)


    def export_pdf(self):
        self.ensure_one()
        context = self._context
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('as_bo_hr.as_planilla_afp_pdf_doc').report_action(self, data=data)