# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class HrContract(models.Model):
    """Hr Contract."""

    _inherit = "hr.contract"

    @api.depends('employee_id.address_home_id.vat')
    def _compute_identification_id(self):
        for rec in self:
            if rec.employee_id.address_home_id.vat:
                rec.identification_id = rec.employee_id.address_home_id.vat

    # leave_generate_id = fields.Many2one(
    #    'hr.leaves.generate', 'Leave Generate')
    identification_id = fields.Char(
        compute='_compute_identification_id', string='Identification No',
        store=True, tracking=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Structure',
                                readonly=True, states={'draft': [('readonly', False)]}, tracking=True,
                                help='Defines the rules that have to be applied to this payslip, accordingly '
                                     'to the contract chosen. If you let empty the field contract, this field isn\'t '
                                     'mandatory anymore and thus the rules applied will be all the rules set on the '
                                     'structure of all contracts of the employee valid for the chosen period')
