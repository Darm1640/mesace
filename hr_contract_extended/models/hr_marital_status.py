# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrMaritalStatus(models.Model):
    _name = 'hr.marital.status'
    _description = 'Marital Status'

    name = fields.Char('Name', required=True)
