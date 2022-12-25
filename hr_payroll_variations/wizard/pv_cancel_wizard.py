# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import timedelta, date


class pvCancelWizard(models.TransientModel):
    _name = 'hr.pv.cancel.wizard'
    _description = 'pv Cancel Wizard'

    date = fields.Datetime(string="Date Cancel")

    
    def confirm(self):
        active_id = self.env.context.get('active_id')
        pv_id = self.env['hr.pv'].browse(active_id)
        if pv_id.deduction_employee_id:
            pv_id.deduction_employee_id.write({
                            'active': False})
        pv_id.write({
            'cancel_date': self.date,
            'state': 'cancel'})


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
