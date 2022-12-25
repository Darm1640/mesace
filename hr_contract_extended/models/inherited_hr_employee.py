# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    marital_status_id = fields.Many2one('hr.marital.status', string="Marital",
                                        tracking=True)
    required_restriction = fields.Boolean('Required Restriction', defaut=True,
                                          tracking=True)
    previous_regimen = fields.Boolean('Previous Regimen', defaut=True,
                                      tracking=True)
    entry_date = fields.Date('Entry Date', tracking=True)
    seniority = fields.Char(compute="_compute_seniority")
    end_date_eps = fields.Date(tracking=True)

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        return res

    def create_user(self):
        user_id = self.env['res.users'].create({
            'name': self.name,
            'login': self.work_email,
            'employee_id': self.id,
        })
        partner = user_id.partner_id
        user_id.write({'partner_id': self.address_home_id.id})
        partner.unlink()
        self.write({
            'user_id': user_id.id,
            'address_home_id': user_id.partner_id.id})

    @api.depends('entry_date')
    def _compute_seniority(self):
        for employee in self:
            if employee.entry_date:
                today = str(fields.date.today()) + ' ' + '00:00:00'
                entry_date = str(employee.entry_date) + ' ' + '00:00:00'
                start = datetime.strptime(entry_date, '%Y-%m-%d %H:%M:%S')
                ends = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(ends, start)
                diff_str = "%d days %d month %d years" % (
                    diff.days, diff.months, diff.years)
                employee.seniority = diff_str
            else:
                employee.seniority = ''
