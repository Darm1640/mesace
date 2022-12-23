# -*- coding: utf-8 -*-
import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[("autotizada", "Autorizada")], ondelete={'autotizada': 'cascade'})

    # Por favor revisar por catita
    def _as_get_type_document(self):
        for order in self:
            as_type_saldo = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_modalidad'))
            as_limite_pago = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limite_pago'))
            order.as_type_docu = as_type_saldo
            # if order.as_type_docu == 'Factura-Venta':
            #     order.as_porcentaje = as_limite_pago
            # else:
            #     order.as_porcentaje = 0.0SO/2021/00116
    def as_open_form(self):
        for sale in self:
            sale.invoice_status = 'to invoice'
    @api.model
    def create(self, vals):
        line = super(SaleOrder, self).create(vals)
        impuesto = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limite_pago')
        line.as_porcentaje = float(impuesto)
        return line

    as_type_docu = fields.Char(string='Tipo Documento', compute="_as_get_type_document")
    as_porcentaje = fields.Float('Porcentaje Factura', help=u'Porcentaje para generar Facturas.')
    as_saldo = fields.Float('Saldo General', help=u'Saldo por pagar de la venta.')
    as_saldo_sale = fields.Float('Importe Adeudado', help=u'Saldo por pagar de la venta.')
    as_pagado = fields.Float('Pagos', help=u'Pagos realizados en la venta.')
    payment_count = fields.Integer(string='Cant. Pagos', compute='_compute_payment')

    def stat_pagos(self):
        self.ajustar_saldos(False)

    def stat_saldo(self):
        self.ajustar_saldos(False)

    def action_confirm(self):
        vals = super(SaleOrder, self).action_confirm()
        for order in self:
            order.ajustar_saldos(True)
        return vals

    def ajustar_saldos(self, bandera):
        for order in self:
            monto_pagado = 0.00
            total_saldo = 0.00
            #pagos en factutas
            for inv in order.invoice_ids:
                for payment in inv.sudo()._get_reconciled_info_JSON_values():
                    monto_pagado += order.currency_id._convert(payment['amount'],order.currency_id, order.company_id, order.date_order,round=False)
            #pagos en Ventas
            monto_asientos = self.as_control_saldo_sale(order.partner_id.property_account_receivable_id,order)
            monto_asiento_sale = self.as_control_saldo_sale(order.partner_id.property_account_receivable_id,order)
            monto_pagado +=order.company_id.currency_id._convert(monto_asientos,order.currency_id, order.company_id, order.date_order,round=False)
            #actualizar saldo de la venta individual 
            as_type_saldo = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_modalidad'))
            as_limite = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limite_pago'))
            if as_type_saldo == 'Factura':
                monto_venta = 0.0
            elif as_type_saldo == 'Venta':
                monto_venta = order.amount_total
            else:
                as_factor = 100-as_limite
                monto_venta = order.amount_total * (as_factor/100)
            
            order.as_saldo_sale = monto_venta - monto_asiento_sale

            #saldo general de la venta
            total_saldo = order.amount_total - monto_pagado
            amount_access = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_amount_access'))
            amount_access = order.company_id.currency_id._convert(amount_access,order.currency_id, order.company_id, order.date_order,round=False)
            if total_saldo >= (amount_access*-1) and total_saldo <= amount_access:
                total_saldo = 0.0
            if order.id:
                self.env.cr.execute('UPDATE sale_order SET as_pagado='+str(monto_pagado)+' , as_saldo='+str(total_saldo)+' WHERE id='+str(order.id))
        return True

    def action_view_payment(self):
        account_id = self.partner_id.property_account_receivable_id.id
        pay_records = self.env['account.move.line']
        sale_payment_ids = self.env['account.move.line'].sudo().search([('sale_id', '=', self.id),('move_id.state', '=', 'posted'),('account_id', '=', account_id)])
        pay_records |= sale_payment_ids
        for inv in self.invoice_ids:
            invoice_payment_ids = self.env['account.move.line'].sudo().search([('invoice_id', '=', inv.id),('move_id.state', '=', 'posted'),('account_id', '=', account_id)])
            for payment in invoice_payment_ids:
                pay_records |= payment
        return {
            'name': _('Pagos realizados'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', pay_records.ids)],
        }

    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_payment(self):
        for order in self:
            account_id = order.partner_id.property_account_receivable_id.id
            pay_records = self.env['account.move.line']
            pay_records |= self.env['account.move.line'].sudo().search([('sale_id', '=', self.id),('move_id.state', '=', 'posted'),('account_id', '=', account_id)])
            for inv in self.invoice_ids:
                invoice_payment_ids = self.env['account.move.line'].sudo().search([('invoice_id', '=', inv.id),('move_id.state', '=', 'posted'),('account_id', '=', account_id)])
                for payment in invoice_payment_ids:
                    pay_records |= payment
            order.payment_count = len(pay_records.ids)

    def as_control_saldo_sale(self,account_id,sale):
        total = 0.0
        resultado = 0.0
        account_query = ("""
            SELECT debit,credit from account_move_line aml 
            join account_move am on am.id = aml.move_id
            where am.state='posted' and aml.sale_id = """ +str(sale.id)+ """ and aml.account_id= """ +str(account_id.id)+ """ order by am.date asc """)
        self.env.cr.execute(account_query)
        total = 0.0
        for move_line in self.env.cr.fetchall():
            resultado = float(move_line[1])
            total += resultado
        return total

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        currency_id = self.env.user.company_id.currency_id
        if self.order_id.as_type_docu == 'Factura-Venta':
            impuesto = float(self.order_id.as_porcentaje)
            price_unit = self.price_unit * (impuesto/100)
            res.update({'price_unit': self.order_id.currency_id._convert(price_unit, currency_id,self.order_id.company_id, self.order_id.date_order,round=True)})
        return res
