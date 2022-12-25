# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class pvRejectWizard(models.TransientModel):
    _name = 'hr.pv.reject.wizard'
    _description = 'pv Reject Wizard'

    reject_reason = fields.Text(string="Reject Reason")

    
    def confirm(self):
        active_id = self.env.context.get('active_id')
        pv_id = self.env['hr.pv'].browse(active_id)
        pv_id.write({
            'reject_reason': self.reject_reason,
            'state': 'rejected'})


class pvCheckDateWizard(models.TransientModel):
    _name = 'hr.pv.check.date.wizard'
    _description = 'pv Check Date'

    
    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    message = fields.Text(
        string="Message",
        readonly=True,
        default=get_message)
