# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil import relativedelta
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)
      

class PurchaseOrderLine_invoice(models.Model):
    _inherit = 'purchase.order.line'

    as_price_unit_import = fields.Float(string="Costo importacion actualizado")
    
    @api.model
    def _prepare_account_move_line(self, move=False):
        invoice=0.00
        valor = super(PurchaseOrderLine_invoice, self)._prepare_account_move_line(move=False)
        valor['as_discount_amount'] = self.as_descuento_linea 
        valor['as_price_total_aux'] = self.as_type_total
        valor['as_price_unit_aux'] = self.price_unit
        valor['price_unit'] = self.price_unit
        if (self.price_unit*self.product_qty) > 0:
            value = (self.as_descuento_linea*100)/(self.price_unit*self.product_qty)
            valor['discount'] = value
        return valor

class Stockmove(models.Model):
    _inherit = 'stock.move'

    as_price_unit_import = fields.Float(string="Costo importacion actualizado")
    