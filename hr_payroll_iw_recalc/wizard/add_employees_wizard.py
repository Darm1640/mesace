# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AddEmployeesWizard(models.TransientModel):
    """Add Employees Wizard."""

    _name = "add.employees.wizard"

    employee_ids = fields.Many2many(
        'hr.employee')

    def generate_employees(self):
        """Generate line based on the employees."""
        for rec in self:
            for employee in rec.employee_ids:
                self.env['hr.recalc.lines'].create({
                    'employee_id': employee.id,
                    'hr_payslip_iw_recalc_id':
                        rec._context.get('active_id', '')})
