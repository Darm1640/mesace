# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Hrpv(models.Model):
    _inherit = 'hr.pv'

    reason_payroll_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason', 'Reason payroll',
        domain="[('type', '=', 'payroll')]", tracking=True)
    reason_talent_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason', 'Reason talent',
        domain="[('type', '=', 'talent')]", tracking=True)
    contract_completion_id = fields.Many2one(
        'hr.contract.completion', 'Contract Completion',
        tracking=True)

    def _create_record(self):
        if self.subtype_id == self.env.ref(
                'hr_payroll_variations.pv_subtype_TERM_CONTR'):
            message = self.create_contract_completion()
            # self.message_post(
            #    body=message,
            #    partner_ids=self.message_follower_ids)
        return super(Hrpv, self)._create_record()

    def create_contract_completion(self):
        contract = self.env['hr.contract.completion'].create({
            'employee_id': self.employee_id.id,
            'date': self.start_date.replace(hour=0, minute=00),
            'unjustified': self.event_id.unjustified,
            'state': 'draft',
            'pv_id': self.id,
            'withdrawal_reason_id': self.reason_payroll_id and self.reason_payroll_id.id or False
        })
        self.contract_completion_id = contract.id
        return _("A new Contract Completion has been created")
