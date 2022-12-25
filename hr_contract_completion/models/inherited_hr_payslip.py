# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    contract_completion_id = fields.Many2one('hr.contract.completion')
    unjustified = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)]})

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        if self.contract_completion_id:
            self.contract_completion_id.state = 'paid'
        hr_pv_rec = self.env['hr.pv'].search(
            [('start_date', '>=', self.date_from),
             ('start_date', '<=', self.date_to),
             ('state', 'in', ['wait', 'wait_comments']),
             ('employee_id', '=', self.employee_id.id),
             ('subtype_id', '!=', self.env.ref(
                 'hr_payroll_variations.pv_subtype_FIJ').id)])
        for pv in hr_pv_rec:
            if pv.check_approver():
                pv.action_approve()
        hr_pv_rec = self.env['hr.pv'].search(
            [('start_date', '>=', self.date_from),
             ('start_date', '<=', self.date_to),
             ('state', '=', 'approved'),
             ('employee_id', '=', self.employee_id.id),
             ('is_user_appr', '!=', False),
             ('subtype_id', '!=', self.env.ref(
                 'hr_payroll_variations.pv_subtype_FIJ').id)])
        for pv in hr_pv_rec:
            pv.action_process()
        return res
