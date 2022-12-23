# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class as_account_move(models.Model):
    _inherit = 'account.move'

    @api.onchange('as_tipo_retencion','as_tipo_documento')
    def as_get_retencion_invoice(self):
        for inv in self:
            inv.partner_id.as_tasas = inv.as_tasas
            inv.partner_id.as_interes = (inv.as_interes)/(inv.as_get_porcentaje()or 1)
            if inv.move_type == 'in_invoice':
                for line in inv.invoice_line_ids:
                    if inv.as_tipo_retencion.as_taxes_ids.ids != []:
                        line.tax_ids = inv.as_tipo_retencion.as_taxes_ids.ids
                    elif self.as_tipo_documento !='Factura':
                        line.tax_ids = False
                    else:
                        line.tax_ids = line.product_id.supplier_taxes_id.ids
                    line.recompute_tax_line = True
                    line._onchange_price_subtotal()
                inv._onchange_invoice_line_ids()
                inv._recompute_tax_lines()

    @api.onchange('as_tipo_factura','as_tasas','as_interes')
    def as_get_retencion_factura(self):
        for inv in self:
            inv.partner_id.as_tasas = inv.as_tasas
            inv.partner_id.as_interes = (inv.as_interes)/(inv.as_get_porcentaje()or 1)
            if inv.move_type == 'in_invoice':
                for line in inv.invoice_line_ids:
                    if inv.as_tipo_factura.as_taxes_ids.ids != []:
                        line.tax_ids = inv.as_tipo_factura.as_taxes_ids.ids
                    elif self.as_tipo_documento !='Factura':
                        line.tax_ids = False
                    else:
                        line.tax_ids = line.product_id.supplier_taxes_id.ids
                    line.recompute_tax_line = True
                    line._onchange_price_subtotal()
                inv._onchange_invoice_line_ids()
                inv._recompute_tax_lines()


    def write(self, vals):
        res = super().write(vals)
        for x in self:
            if x.move_type == 'in_invoice':
                x.partner_id.as_tasas = x.as_tasas

                x.partner_id.as_interes = (x.as_interes)/(x.as_get_porcentaje()or 1)
        return res
        
    def as_get_porcentaje(self):
        total = 0
        for line in self.invoice_line_ids:
            total += line.price_unit*line.quantity 
        return total
    
class as_account_move_line(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def as_get_retencion(self):
        for line in self:
            if line.move_id.move_type == 'in_invoice':
                if line.move_id.as_tipo_retencion.as_taxes_ids.ids != []:
                    line.tax_ids = line.move_id.as_tipo_retencion.as_taxes_ids.ids
                else:
                    line.tax_ids = line.product_id.supplier_taxes_id.ids
                if line.move_id.as_tipo_factura.as_taxes_ids.ids != []:
                    line.tax_ids = line.move_id.as_tipo_factura.as_taxes_ids.ids
                else:
                    line.tax_ids = line.product_id.supplier_taxes_id.ids
                line.recompute_tax_line = True
                line._onchange_price_subtotal()


