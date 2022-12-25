# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    pv_ref = fields.Char(
        'pv Reference',
        copy=False, readonly=True)
    is_eps = fields.Boolean(string='EPS')
    is_arl = fields.Boolean(string='ARL')
    allow_collision = fields.Boolean('Allow Collision')
    

    @api.constrains('date_from', 'date_to', 'state', 'employee_id')
    def _check_date(self):
        for holiday in self.filtered('employee_id'):
            domain = [
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('allow_collision', '=', False),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays and not self.allow_collision:
                raise ValidationError(_('You can not set 2 times off that overlaps on the same day for the same employee.'))

