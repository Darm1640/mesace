# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _


class AsPurchaseOrder(models.Model):
    """Modulo heredado para agregar funcionalidad de boton inteligente en compras"""
    _inherit = "purchase.order"

    as_project_id = fields.Many2one('project.task', string="Proyecto")
    as_permiso_cancelar = fields.Boolean(string='Cancelar compra', default=False)
