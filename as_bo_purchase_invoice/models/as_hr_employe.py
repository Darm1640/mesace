# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, _
class HrExpense(models.Model):
    _inherit = "hr.employee"

    as_firma_archivo = fields.Binary(string="Firma" )