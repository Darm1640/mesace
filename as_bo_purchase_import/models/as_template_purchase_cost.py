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
    _name = 'stock.landed.template'
    _description = "Plantilla de costos de importacion"

    name = fields.Char('Nombre')
    template_cost_lines = fields.One2many('stock.landed.template.lines', 'template_cost_id', string='Cost Lines')

class stocktemplatelines(models.Model):
    _name = 'stock.landed.template.lines'
    _description = "Plantilla de costos de importacion productos tipo gastos de envio"

    name = fields.Char('Description')
    template_cost_id = fields.Many2one('stock.landed.template', 'Landed Cost',required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', required=True,domain=[('landed_cost_ok', '=', True)])
    price_unit = fields.Float('Cost', digits=dp.get_precision('Product Price'), required=True)
    price_unit_est = fields.Float('Costo Estimado', digits=dp.get_precision('Product Price'), required=True)
    split_method = fields.Selection(product.SPLIT_METHOD, string='Split Method', required=True)
    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])
    as_facturado = fields.Boolean(string="Facturado", default=False)

    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.price_unit = 0.0
        self.name = self.product_id.name or ''
        self.split_method = self.product_id.split_method_landed_cost or 'equal'
        self.price_unit = self.product_id.standard_price or 0.0
        self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id

