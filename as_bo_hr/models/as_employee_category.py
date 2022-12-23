# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class hremployeecategory(models.Model):
    _inherit = "hr.employee.category"

    as_tipo = fields.Selection([('Costo', 'Costo'),('Gasto', 'Gasto')], default='Costo',string='Tipo')