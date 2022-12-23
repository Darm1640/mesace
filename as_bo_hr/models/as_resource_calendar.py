# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.osv.expression import AND
from odoo.tools import float_compare
from odoo import models, fields, api


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    as_total_days = fields.Float( string="Dias totales al mes")
    as_tiempo_tolerancia = fields.Float( string="Dias de Tolerancia")
    as_modalidad = fields.Boolean(string="Cantidad de Dias y horas fijos para calculo")