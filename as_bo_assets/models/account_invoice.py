# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    # @api.one
    def asset_create(self):
        if self.asset_category_id:
            #fecha compra
            fecha = self.move_id.invoice_date.strftime('%Y-%m-%d')
            if self.purchase_line_id:
                fecha = self.purchase_line_id.order_id.date_order.strftime('%Y-%m-%d')
            vals = {
                'name': self.name,
                'code': self.move_id.name or False,
                'category_id': self.asset_category_id.id,
                'value': self.price_subtotal,
                'partner_id': self.move_id.partner_id.id,
                'company_id': self.move_id.company_id.id,
                'currency_id': self.move_id.company_currency_id.id,
                'date': self.move_id.date.strftime('%Y-%m-%d'),
                'invoice_id': self.move_id.id,
                'product_id': self.product_id.id,
                'first_depreciation_manual_date': fecha,
            }
            changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['account.asset.asset'].create(vals)
            # if self.asset_category_id.open_asset:
            #     asset.validate()
        return True
