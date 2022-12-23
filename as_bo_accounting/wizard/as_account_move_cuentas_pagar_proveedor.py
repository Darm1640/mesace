# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime

from time import mktime
import logging
from datetime import datetime, timedelta
from datetime import datetime
class StockQuantityHistory(models.TransientModel):
    _name = 'as.stock.quantity.history'
    date = fields.Date(string='Fecha de Vencimiento', required=True, default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'))

    def open_table(self):
        pago_ids=self.env['account.move'].search([('state','=',"posted"),("invoice_date_due",'=',self.date),("move_type","=","in_invoice")])
        action_picking = self.env.ref('account.action_move_in_invoice_type')
        action = action_picking.read()[0]
        action['context'] = {}
        action['domain'] = [('id', 'in', pago_ids.ids)]
        return action
       