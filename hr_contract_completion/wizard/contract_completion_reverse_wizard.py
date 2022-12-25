# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ContractCompletionReverseWizard(models.TransientModel):
    _name = 'hr.contract.completion.reverse.wizard'
    _description = 'Contract Completion Reverse Wizard'

    reverse_reason = fields.Text(string="Reverse Reason")

    def confirm(self):
        active_id = self.env.context.get('active_id')
        contract_completion_id = \
            self.env['hr.contract.completion'].browse(active_id)
        contract_completion_id.write({
            'reverse_reason': self.reverse_reason,
        })
