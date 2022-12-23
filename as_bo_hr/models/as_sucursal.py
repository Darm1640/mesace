# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, _
class HrSucursal(models.Model):
    _name = "as.sucursal"

    name = fields.Char(string="Nombre De la Sucursal")
