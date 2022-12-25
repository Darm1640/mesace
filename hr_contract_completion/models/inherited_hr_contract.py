# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from odoo import api, fields, models


class HrContract(models.Model):
    """Add reason in the contract."""

    _inherit = 'hr.contract'

    contract_completion_id = fields.Many2one('hr.contract.completion', tracking=True)
    reason_payroll_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason',
        'Reason for Payroll Withdrawal', tracking=True)
    reason_talent_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason',
        'Reason for Talent withdrawal', tracking=True)
