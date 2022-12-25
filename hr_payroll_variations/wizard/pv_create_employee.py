# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class pvCreateEmployee(models.TransientModel):
    _name = 'pv.create.employee'
    _description = 'pv Create Employee'

    work_email = fields.Char()
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job Position')
    parent_id = fields.Many2one('hr.employee', 'Manager')
    birthday = fields.Date('Date of Birth')
    address_id = fields.Many2one(
        'res.partner', 'Work Address',
        default=lambda self: self.env.user.company_id.partner_id)
    job_title = fields.Char()

    @api.onchange('job_id')
    def onchange_job_id(self):
        """Fill Job."""
        if self.job_id and self.job_id.name:
            self.job_title = self.job_id.name

    
    def confirm(self):
        """Create Employee."""
        active_id = self.env.context.get('active_id')
        pv_id = self.env['hr.pv'].browse(active_id)
        if pv_id.contact_id:
            employee = self.env['hr.employee'].create({
                'name': pv_id.contact_id.name,
                'work_email': self.work_email,
                'department_id': self.department_id.id,
                'job_id': self.job_id.id,
                'job_title': self.job_title,
                'address_home_id': pv_id.contact_id.id,
            })
            pv_id.write({
                'employee_id': employee.id})
