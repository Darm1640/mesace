# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrLeaveCode(models.Model):
    """Hr Leave Code."""

    _name = 'hr.leave.code'
    _description = 'Hr Leave Code'
    _rec_name = 'code'

    name = fields.Char()
    code = fields.Char()
