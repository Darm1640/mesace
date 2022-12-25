# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class HrLeaveType(models.Model):
    """Hr Leave Type."""

    _inherit = "hr.leave.type"

    vacation_pay_31 = fields.Boolean("Vacation Pay 31")
    is_sumar_en_nomina = fields.Boolean("Sumar en Nomina")
    no_count_in_payroll = fields.Boolean("No Count In Payroll")
    autocalculate_leave = fields.Boolean('Auto Calculate Leave', default=False)
    no_count_rent = fields.Boolean('No Count Rent', default=False)
    exclude_calculate_payslip = fields.Boolean('Exclude Calculate Payslip', default=False)
    autogenerate_from_payslip = fields.Boolean('Autogenerate From Payslip', default=False)


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def write(self, vals):
        res = super(HrLeave, self).write(vals)
        self.employee_id.calculate_leaves_details()
        return res

    @api.model
    def create(self, vals):
        res = super(HrLeave, self).create(vals)
        res.employee_id.calculate_leaves_details()
        return res


class HRLeaveReport(models.Model):
    _inherit = "hr.leave.report"

    number_of_days = fields.Float('Days', digits=(32, 4),
                                  tracking=True)


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip')
    number_of_days_display = fields.Float('Days', digits=(32, 4),
                                          tracking=True)

    def write(self, vals):
        res = super(HolidaysAllocation, self).write(vals)
        self.employee_id.calculate_leaves_details()
        return res

    @api.model
    def create(self, vals):
        res = super(HolidaysAllocation, self).create(vals)
        res.employee_id.calculate_leaves_details()
        return res
