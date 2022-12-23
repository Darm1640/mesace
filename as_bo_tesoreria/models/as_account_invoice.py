# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
import qrcode
import tempfile
import base64
#Convertir numeros en texto
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time
from time import mktime
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

import ast
import json
import re
import warnings

from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
class AccountInvoice(models.Model):
    _inherit = 'account.move'

    as_tipo_fact  = fields.Selection([('CajaChica','Caja Chica'),('Proveedor','Proveedor')] ,'Tipo de Factura', help=u'Tipo de documento que pertenece la factura.', default='Proveedor')
    as_porcentaje = fields.Float(string='Porcentaje aplicado',default=0.0)
    state = fields.Selection(selection_add=[('Regularizar', 'Regularizar')], ondelete={'Regularizar': 'cascade'})
    as_is_gasto = fields.Boolean(string='Es factura de gasto',default=False)

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        if self.as_is_gasto:
            raise UserError(_("No se puede pagar una factura de este Tipo (GASTO)"))
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if move.state in ('posted','Regularizar') and move.is_invoice(include_receipts=True):
                payments_widget_vals['content'] = move._get_reconciled_info_JSON_values()

            if payments_widget_vals['content']:
                move.invoice_payments_widget = json.dumps(payments_widget_vals, default=date_utils.json_default)
            else:
                move.invoice_payments_widget = json.dumps(False)
   
    def as_action_invoice_regularizar(self):
        self.as_contable = True
        if self.state == 'draft':
            self.action_post()
            self.state = 'Regularizar'
        else:
            self.state = 'Regularizar'    
    
    def as_button_draft(self):
        self.as_contable = False
        self.state = 'draft'

    def as_action_invoice_regularizar_move(self):
        self.as_si_contable = True
        if self.state == 'draft':
            self.action_post()
            self.state = 'Regularizar'
        else:
            self.state = 'Regularizar'

    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        if self.move_id:
            for line in self.move_id.line_ids:
                line.invoice_id = self.id

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        monto_it=0.0
        if self.type != 'out_invoice':  
            if self.as_tipo_factura.as_is_combustible:
                for item in res:
                    monto_it = (item['price']*(1-(self.as_tipo_factura.as_factor/100))*0.87+(item['price']*(self.as_tipo_factura.as_factor/100)))
                    item['price'] = monto_it
                    item['price_unit'] = monto_it
        return res


    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()
        monto_it=0.0
        if self.type != 'out_invoice':  
            if self.as_tipo_factura.as_is_combustible:
                for item in res:
                    monto_it = (self.amount_total*(1-(self.as_tipo_factura.as_factor/100))*0.13)
                    item['price'] = monto_it
                    item['price_unit'] = monto_it
                # monto_it = (self.amount_total*(1-(self.as_tipo_factura.as_factor/100))*0.13)
                # move_line_dict = {
                #     'type': 'tax',
                #     'name':self.as_tipo_factura.name,
                #     'price_unit':  round(monto_it,2),
                #     'quantity': 1,
                #     'price': round(monto_it,2),
                #     'account_id': self.as_tipo_factura.as_account.id,
                #     'invoice_id': self.id,
                #     }
                # res.append(move_line_dict)
        return res


    @api.depends('amount_residual', 'state')
    def _compute_payment(self):
        for order in self:
            account_id = order.partner_id.property_account_receivable_id.id
            pay_records = self.env['account.move.line']
            pay_records |= self.env['account.move.line'].sudo().search([('invoice_id', '=', self.id),('move_id.state', '=', 'posted'),('account_id', '=', account_id)])
            order.payment_count = len(pay_records.ids)

    payment_count = fields.Integer(string='Payments', compute='_compute_payment')

    def as_control_saldo_sale(self,account_id,sale):
        total = 0.0
        resultado = 0.0
        account_query = ("""
            SELECT debit,credit from account_move_line aml 
            join account_move am on am.id = aml.move_id
            where am.state='posted' and aml.invoice_id = """ +str(sale.id)+ """ and aml.account_id= """ +str(account_id.id)+ """ order by am.date asc """)
        self.env.cr.execute(account_query)
        total = 0.0
        for move_line in self.env.cr.fetchall():
            resultado = float(move_line[0])-float(move_line[1])
            total += resultado
        return total

    def ajustar_saldos(self, bandera):
        for order in self:
            monto_pagado = 0.00
            total_saldo = 0.00
            monto_asientos = self.as_control_saldo_sale(order.partner_id.property_account_receivable_id,order)
            monto_pagado +=order.company_id.currency_id._convert(monto_asientos*-1,order.currency_id, order.company_id, order.invoice_date,round=False)
            total_saldo = order.amount_total - monto_pagado
            if order.id:
                self.env.cr.execute('UPDATE account_move SET  amount_residual='+str(total_saldo)+' WHERE id='+str(order.id))
        return True

    def action_view_payment(self):
        account_id = self.partner_id.property_account_receivable_id.id
        pay_records = self.env['account.move.line']
        invoice_payment_ids = self.env['account.move.line'].sudo().search([('invoice_id', '=', self.id),('move_id.state', '=', 'posted'),('account_id', '=', account_id)])
        pay_records |= invoice_payment_ids
        return {
            'name': _('Pagos realizados'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', pay_records.ids)],
        }

    def actualizar_amount_residual(self):
        self.ajustar_saldos(False)
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = "sequence"

    invoice_id = fields.Many2one('account.move', string='Factura')
    as_liquidado_move =  fields.Boolean(string="Esta Liquidado",default=False)
    purchase_id = fields.Many2one('purchase.order', string='Pedido de Compra')
    sale_id = fields.Many2one('sale.order', string='Pedido de Venta')

    def reconcile(self):
        results = {}

        if not self:
            return results

        # List unpaid invoices
        not_paid_invoices = self.move_id.filtered(
            lambda move: move.is_invoice(include_receipts=True) and move.payment_state not in ('paid', 'in_payment')
        )

        # ==== Check the lines can be reconciled together ====
        company = None
        account = None
        for line in self:
            if line.reconciled:
                raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
            if not line.account_id.reconcile and line.account_id.internal_type != 'liquidity':
                raise UserError(_("Account %s does not allow reconciliation. First change the configuration of this account to allow it.")
                                % line.account_id.display_name)
            # if line.move_id.state != 'posted':
            #     raise UserError(_('You can only reconcile posted entries.'))
            if company is None:
                company = line.company_id
            elif line.company_id != company:
                raise UserError(_("Entries doesn't belong to the same company: %s != %s")
                                % (company.display_name, line.company_id.display_name))
            if account is None:
                account = line.account_id
            elif line.account_id != account:
                raise UserError(_("Entries are not from the same account: %s != %s")
                                % (account.display_name, line.account_id.display_name))

        sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))

        # ==== Collect all involved lines through the existing reconciliation ====

        involved_lines = sorted_lines
        involved_partials = self.env['account.partial.reconcile']
        current_lines = involved_lines
        current_partials = involved_partials
        while current_lines:
            current_partials = (current_lines.matched_debit_ids + current_lines.matched_credit_ids) - current_partials
            involved_partials += current_partials
            current_lines = (current_partials.debit_move_id + current_partials.credit_move_id) - current_lines
            involved_lines += current_lines

        # ==== Create partials ====

        partials = self.env['account.partial.reconcile'].create(sorted_lines._prepare_reconciliation_partials())

        # Track newly created partials.
        results['partials'] = partials
        involved_partials += partials

        # ==== Create entries for cash basis taxes ====

        is_cash_basis_needed = account.user_type_id.type in ('receivable', 'payable')
        if is_cash_basis_needed and not self._context.get('move_reverse_cancel'):
            tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
            results['tax_cash_basis_moves'] = tax_cash_basis_moves

        # ==== Check if a full reconcile is needed ====

        if involved_lines[0].currency_id and all(line.currency_id == involved_lines[0].currency_id for line in involved_lines):
            is_full_needed = all(line.currency_id.is_zero(line.amount_residual_currency) for line in involved_lines)
        else:
            is_full_needed = all(line.company_currency_id.is_zero(line.amount_residual) for line in involved_lines)

        if is_full_needed:

            # ==== Create the exchange difference move ====

            if self._context.get('no_exchange_difference'):
                exchange_move = None
            else:
                exchange_move = involved_lines._create_exchange_difference_move()
                if exchange_move:
                    exchange_move_lines = exchange_move.line_ids.filtered(lambda line: line.account_id == account)

                    # Track newly created lines.
                    involved_lines += exchange_move_lines

                    # Track newly created partials.
                    exchange_diff_partials = exchange_move_lines.matched_debit_ids \
                                             + exchange_move_lines.matched_credit_ids
                    involved_partials += exchange_diff_partials
                    results['partials'] += exchange_diff_partials

                    exchange_move._post(soft=False)

            # ==== Create the full reconcile ====

            results['full_reconcile'] = self.env['account.full.reconcile'].create({
                'exchange_move_id': exchange_move and exchange_move.id,
                'partial_reconcile_ids': [(6, 0, involved_partials.ids)],
                'reconciled_line_ids': [(6, 0, involved_lines.ids)],
            })

        # Trigger action for paid invoices
        not_paid_invoices\
            .filtered(lambda move: move.payment_state in ('paid', 'in_payment'))\
            .action_invoice_paid()

        return results             