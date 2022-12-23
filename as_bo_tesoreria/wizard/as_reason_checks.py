# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsReasonWiz(models.Model):
    """Wizard para llenar motivo tanto de anulacion como de protesta"""
    _name = 'as.reason.check.wiz'
    _description="Wizard para llenar motivo tanto de anulacion como de protesta"
    _order = 'as_reason'

    as_reason = fields.Many2one('as.reason.checks', string="Motivo")
    as_control = fields.Many2one('as.check.control', string="Cheque")
    as_action = fields.Char(string="Action")
    as_action_view = fields.Char(string="Acción")
    as_date_expire = fields.Date("Fecha de Prorroga", default=fields.Date.today)

    @api.model
    def default_get(self, fields):
        res = super(AsReasonWiz, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        action = self._context.get('default_as_action')
        res['as_control'] = self._context.get('active_id')
        as_modelo = self._context.get('active_model')
        cheque = self.env[as_modelo].search([('id','in',res_ids)])
        if action == 'protested':
            res['as_action_view'] = 'PROTESTAR'
        elif action == 'cancel':
            res['as_action_view'] = 'CANCELAR'
        else:
            res['as_action_view'] = 'PRORROGAR'
        if cheque:
            pass
        return res
    
    def as_process_checks(self):
        cheque = self.as_control
        if self.as_action in ('protested','cancel'):
            cheque.as_reason = self.as_reason
            cheque.state = self.as_action
        else:
            cheque.as_date_expire = self.as_date_expire
            cheque.as_reason = self.as_reason
            cheque.state = 'extended'
        return True




