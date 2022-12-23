# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.tools import formatLang

class SaleBillUnion(models.Model):
    _name = 'as.sale.invoice.auto'
    _auto = False
    _description = 'Union Factura y Venta'
    _order = "date desc, name desc"

    name = fields.Char(string='Reference', readonly=True)
    reference = fields.Char(string='Source', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    sale_bill_id = fields.Many2one('account.move', string='Cliente Factura', readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'as_sale_invoice_auto')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW as_sale_invoice_auto AS (
                SELECT
                    id, name, ref as reference, partner_id, date, amount_total as amount, currency_id, company_id,
                    id as sale_bill_id, NULL as sale_order_id
                FROM account_move
                WHERE
                    move_type='out_invoice' and state = 'posted'
            UNION
                SELECT
                    -id, name, client_order_ref as reference, partner_id, date_order::date as date, amount_total as amount, currency_id, company_id,
                    NULL as sale_bill_id, id as sale_order_id
                FROM sale_order
                WHERE
                    state in ('sale', 'done') AND
                    invoice_status in ('to invoice', 'no')
            )""")

    def name_get(self):
        result = []
        for doc in self:
            name = doc.name or ''
            if doc.reference:
                name += ' - ' + doc.reference
            amount = doc.amount
            # if doc.sale_order_id and doc.sale_order_id.invoice_status == 'no':
            #     amount = 0.0
            name += ': ' + formatLang(self.env, amount, monetary=True, currency_obj=doc.currency_id)
            result.append((doc.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('reference', operator, name)]
        purchase_bills_auto_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return purchase_bills_auto_ids
