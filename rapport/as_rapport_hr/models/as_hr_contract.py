# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class Ascontract(models.Model):
    _inherit = "hr.contract"

    as_anio = fields.Integer(string='Años Antiguedad Cargo')
    as_mes = fields.Integer(string='Meses Antiguedad Cargo')
    as_dias = fields.Integer(string='Dias Antiguedad Cargo')
    employer_id = fields.Many2one('as.survey.employer', string='Empleador')

    @api.onchange('date_start')
    def _compute_contract_id(self):
        if self.date_start:
            tiempo = fields.Date.context_today(self) - self.date_start
            self.as_mes = int((tiempo.days/30/12 - int(tiempo.days/30/12))*12)
            self.as_dias = int((tiempo.days/30/12 - int(tiempo.days/30/12))*30)
            if int(tiempo.days/30/12) >= 1:
                self.as_anio = int(tiempo.days/30/12)
            else:
                self.as_anio = 0
