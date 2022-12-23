# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    as_numero_patronal = fields.Char(string="Numero Patronal")
    as_patronal_municipal = fields.Char(string="Padrón Municipal")
