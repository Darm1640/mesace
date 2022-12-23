# -*- coding: utf-8 -*-
##############################################################################

from datetime import datetime, timedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.exceptions import UserError
from odoo.tools.translate import _
import base64
from odoo import netsvc
from odoo import tools
from time import mktime
import logging
from datetime import datetime
from odoo import api, fields, models

class as_product_detail_wiz(models.TransientModel):
    _name="as.duplicate.sale"
    _description = "Duplicar venta by AhoraSoft"
    
    as_partner_id = fields.Many2one('res.partner', string="Cliente")
    as_alias_lugar = fields.Char(string="Lugar", required=True)
    as_venta = fields.Many2one('sale.order', string="Venta")

    def get_sale_process(self):
        lines = []
        move_create = self.env['sale.order']
        for line_sale in self.as_venta.order_line:
                val_line = {
                    'product_id': line_sale.product_id.id,
                    'name': line_sale.name,
                    'product_uom_qty': line_sale.product_uom_qty,
                    'product_uom': line_sale.product_uom.id,
                    'price_unit': line_sale.price_unit,
                    'tax_id': line_sale.tax_id.ids,
                    'display_type':line_sale.display_type,
                    'currency_id': self.as_venta.currency_id.id,

                }
                lines.append((0, 0,val_line))
        move_vals = {
            'partner_id': self.as_partner_id.id,
            'pricelist_id': self.as_venta.pricelist_id.id,
            'note': self.as_venta.note,
            'currency_id': self.as_venta.currency_id.id,
            'as_alias_lugar': self.as_alias_lugar,
            'order_line': lines,
        }
        # move_vals['line_ids']+= line_move 
        move = move_create.create(move_vals)
        move.currency_id = self.as_venta.currency_id