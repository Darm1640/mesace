# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    date_end_required = fields.Boolean()
    hr_contract_alert_id = fields.Many2one(
        'hr.contract.alert', 'Contract Alert')
    trial_period_duration = fields.Integer(copy=False)
