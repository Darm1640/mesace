# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models, fields, tools, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_payslip_lines(self):
        lines = super(HrPayslip, self)._get_payslip_lines()

        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }

        for line in lines:
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})

            rule = self.env['hr.salary.rule'].search([('id', '=', line['salary_rule_id'])])

            if rule:
                line['pv_ids'] = rule._compute_rule_for_pvs(localdict)
               # line['dis_aid_ids'] = rule._compute_rule_for_balance_di_aid(localdict)

        return lines


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    pv_ids = fields.Many2many(
        'hr.pv', 'hr_payslip_hr_pv_rel',
        'payslip_line_id', 'pv_id', string='PVs')
