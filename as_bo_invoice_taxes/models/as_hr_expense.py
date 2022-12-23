# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class hr_expense(models.Model):
    _inherit = 'hr.expense'

    @api.onchange('as_tipo_retencion','as_tipo_documento','as_tipo_factura')
    def as_get_retencion_invoice(self):
        for inv in self:
            if inv.as_tipo_retencion.as_taxes_ids.ids != []:
                inv.tax_ids = inv.as_tipo_retencion.as_taxes_ids.ids
            elif inv.as_tipo_factura.as_taxes_ids.ids != []:
                inv.tax_ids = inv.as_tipo_factura.as_taxes_ids.ids
            elif self.as_tipo_documento !='Factura':
                inv.tax_ids = False
            else:
                inv.tax_ids = inv.product_id.supplier_taxes_id.ids
            

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        taxes=[]
        unit_amount = 0.0
        if self.as_tipo_documento =='Factura':
            for tax in self.tax_ids:
                taxes.append(tax.id)
        else:
            self.tax_ids = []
        if self.as_tipo_retencion.as_taxes_ids.ids != []:
            for tax in self.tax_ids:
                taxes.append(tax.id)
        if self.as_tipo_factura.as_taxes_ids.ids != []:
            for tax in self.tax_ids:
                taxes.append(tax.id)

        if self.as_tipo_factura.as_iva == False:
            unit_amount = self.unit_amount
        else:
            unit_amount =  self.unit_amount       
        res = {
            'name': '%s: %s' % (self.name, self.product_id.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.quantity,
            'as_discount_amount': self.as_descuento_hr,
            'discount': (self.as_descuento_hr*100)/(unit_amount*self.quantity),
            'analytic_account_id': self.analytic_account_id.id,
            'price_unit': unit_amount,
            'tax_ids': [(6, 0, taxes)],
        }
      
        res.update({
            # 'move_id': move.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'partner_id': self.as_supplier_costo.id,
        })
        return res
