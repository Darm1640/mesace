# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    as_sale_invoice_id = fields.Many2one('as.sale.invoice.auto', store=False, readonly=True,
        states={'draft': [('readonly', False)]},
        string='Auto-complete',
        help="Auto-complete Desde Factura Cliente/Venta.")
    as_sale_id = fields.Many2one('sale.order', store=False, readonly=True,
        states={'draft': [('readonly', False)]},
        string='Sale Order',
        help="Auto-complete from a past sale order.")
    as_sale_related_id = fields.Many2one('sale.order', string='Venta')
    as_invoice_ids = fields.Many2many('account.move', 'account_move_id','account_move_id2',states={'draft': [('readonly', False)]},
        string='Facturas Completar',
        help="Auto-complete Desde Factura Cliente/Facturas.",domain="[('state','=','draft'),('move_type','=','out_invoice')]")
    state = fields.Selection(selection_add=[('process', 'Procesado')], ondelete={'process': 'cascade'})

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for inv in self:
            invoice = self.env['as.account.invoice'].search([('as_account_move_id','=',self.id)])
            for inv_rel in invoice:
                inv_rel.as_account_related_id.as_invoice_number = inv.as_invoice_number
        return res

    def as_action_get_invoice(self):
        new_invoice_line_ids = []
        invoices = ''
        for inv in self:
            for inv_get in inv.as_invoice_ids:
                if inv_get.state == 'draft':
                    for inv_get_line in inv_get.invoice_line_ids:
                        create_method = self.env['account.move.line'].with_context(check_move_validity=False).create
                        copied_vals = inv_get_line.copy_data()[0]
                        copied_vals['recompute_tax_line'] = True
                        new_invoice_line_ids.append((0, 0,copied_vals))
                        self.env['as.account.invoice'].create({
                            'as_account_move_id': inv.id,
                            'as_account_related_id': inv_get.id,
                        })
                    inv_get.as_contable = True
                    inv_get.action_post()
                    inv_get.state = 'process'
                    inv_get.as_is_gasto = True
            for invoice in inv.as_invoice_ids:
                invoices += str(invoice.name)+', '
            if new_invoice_line_ids != []:
                inv.write({'invoice_line_ids' : new_invoice_line_ids})
                inv._onchange_invoice_line_ids()
                inv._recompute_tax_lines()
                message = '<b style="color:green">FACTURAS PROCESADAS '+invoices+'</b>'
            else:
                message = '<b style="color:red">FACTURAS YA PROCESADAS '+invoices+'</b>'
            inv.message_post(body=message)
            # inv._recompute_dynamic_lines()
            # # inv._recompute_tax_lines()
                


    @api.onchange('as_sale_related_id')
    def as_get_sale(self):
        for inv in self:
            ids = []
            if inv.move_type == 'out_invoice':
                if inv.as_sale_related_id:
                    inv.as_related_sale_inv(inv.as_sale_related_id,inv)
        

    def as_related_sale_inv(self,sale,invoice):
        cont = 0
        self.invoice_origin = sale.name
        for line_invoice in invoice.invoice_line_ids:
            cont += 1
            if cont < len(sale.order_line):
                sale.order_line[cont].invoice_lines = line_invoice
            else:
                cont-=1
                sale.order_line[cont].invoice_lines = line_invoice
        return True


    def _get_invoice_reference(self):
        self.ensure_one()
        vendor_refs = [ref for ref in set(self.line_ids.mapped('sale_line_id.order_id.client_order_ref')) if ref]
        if self.ref:
            return [ref for ref in self.ref.split(', ') if ref and ref not in vendor_refs] + vendor_refs
        return vendor_refs

    @api.onchange('as_sale_invoice_id', 'as_sale_id')
    def _onchange_purchase_auto_complete(self):
        if self.as_sale_invoice_id.sale_order_id:
            self.as_sale_id = self.as_sale_invoice_id.sale_order_id
        self.as_sale_invoice_id = False

        if not self.as_sale_id:
            return

        # Copy data from PO
        invoice_vals = self.as_sale_id.with_company(self.as_sale_id.company_id)._prepare_invoice()
        invoice_vals['currency_id'] = self.line_ids and self.currency_id or invoice_vals.get('currency_id')
        del invoice_vals['ref']

        # Copy purchase lines.
        po_lines = self.as_sale_id.order_line - self.line_ids.mapped('sale_line_id')
        new_lines = self.env['account.move.line']
        invoice_line_vals = []
        for line in po_lines:
            # new_line = new_lines.create(line._prepare_invoice_line())
            # new_line.account_id = new_line._get_computed_account()
            # new_line._onchange_price_subtotal()
            # new_lines += new_line
            vals = line._prepare_invoice_line(sequence=line.sequence)
            vals['quantity'] = line.product_uom_qty
            invoice_line_vals.append((0, 0, vals,),)
        # new_lines._onchange_mark_recompute_taxes()
        invoice_vals['invoice_line_ids'] += invoice_line_vals
        self.update(invoice_vals)
        for line in self.invoice_line_ids:
            line.account_id = line._get_computed_account()
            line._onchange_price_subtotal()
            line._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('sale_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = self._get_invoice_reference()
        self.ref = ', '.join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self.as_sale_id = False
        self._onchange_currency()
        self.partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id and\
                self.move_type in ['in_invoice', 'in_refund'] and\
                self.currency_id != self.partner_id.property_purchase_currency_id and\
                self.partner_id.property_purchase_currency_id.id:
            if not self.env.context.get('default_journal_id'):
                journal_domain = [
                    ('type', '=', 'sale'),
                    ('company_id', '=', self.company_id.id),
                    ('currency_id', '=', self.partner_id.property_purchase_currency_id.id),
                ]
                default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
                if default_journal_id:
                    self.journal_id = default_journal_id
            if self.env.context.get('default_currency_id'):
                self.currency_id = self.env.context['default_currency_id']
            if self.partner_id.property_purchase_currency_id:
                self.currency_id = self.partner_id.property_purchase_currency_id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.reversed_entry_id:
                continue
            purchase = move.line_ids.mapped('sale_line_id.order_id')
            if not purchase:
                continue
            refs = ["<a href=# data-oe-model=sale.order data-oe-id=%s>%s</a>" % tuple(name_get) for name_get in purchase.name_get()]
            message = _("This vendor bill has been created from: %s") % ','.join(refs)
            move.message_post(body=message)
        return moves

    def write(self, vals):
        # OVERRIDE
        old_purchases = [move.mapped('line_ids.sale_line_id.order_id') for move in self]
        res = super(AccountMove, self).write(vals)
        for i, move in enumerate(self):
            new_purchases = move.mapped('line_ids.sale_line_id.order_id')
            if not new_purchases:
                continue
            diff_purchases = new_purchases - old_purchases[i]
            if diff_purchases:
                refs = ["<a href=# data-oe-model=sale.order data-oe-id=%s>%s</a>" % tuple(name_get) for name_get in diff_purchases.name_get()]
                message = _("This vendor bill has been modified from: %s") % ','.join(refs)
                move.message_post(body=message)
        return res


class as_AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete='set null', index=True)
    as_sale_id = fields.Many2one('sale.order', 'Sale Order', related='sale_line_id.order_id', readonly=True)

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'sale_line_ids' field as well.
        super(as_AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values['sale_line_id'] = self.as_sale_id.id

class AccountMoveLine2(models.Model):
    _name = 'as.account.invoice'
    _description = 'Modelo para almacenar facturas relacionadas'

    as_account_move_id = fields.Many2one('account.move', string='Factura')
    as_account_related_id = fields.Many2one('account.move', string='Relación')