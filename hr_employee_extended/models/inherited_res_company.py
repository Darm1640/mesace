# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    payroll_manager = fields.Many2one("hr.employee", string="Payroll Manager", default=False)
    arl_id = fields.Many2one('res.partner')
