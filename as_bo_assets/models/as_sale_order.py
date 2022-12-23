# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    as_assets = fields.Many2one('account.asset.asset',string='Activo Fijo')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    as_assets = fields.Many2one('account.asset.asset',string='Activo Fijo')

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', [])
        )
        for sale in sale_orders:
            for inv in sale.invoice_ids:
                if sale.as_assets:
                    inv.as_contable = True
        return res
