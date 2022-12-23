# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
#tools
from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
]
class stocktemplate(models.Model):
    _name = 'as.plantillas.template'
    _description = "Plantilla de costos de importacion"

    name = fields.Char('Nombre')
    template_cost_lines = fields.One2many('as.plantillas.template.lines', 'template_cost_id', string='Lineas')

class stocktemplatelines(models.Model):
    _name = 'as.plantillas.template.lines'
    _description = "Plantilla de costos de importacion productos tipo gastos de envio"

    name = fields.Char('Description')
    general_budget_id = fields.Many2one('account.budget.post', 'Posición presupuestaria')
    template_cost_id = fields.Many2one('as.plantillas.template', 'Plantillas customizadas',required=True, ondelete='cascade')
    price_unit = fields.Float('Cost', digits=dp.get_precision('Product Price'), required=True)