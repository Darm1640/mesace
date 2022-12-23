# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)
class AsTesoreria(models.Model):
    _name = 'as.tesoreria'
    _description = 'Tesoreria para pago de ingreso egreso y movimientos de caja'

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    
    name = fields.Char('Titulo',readonly=True)
    state = fields.Selection([('open', 'Abierto'), ('close', 'Cerrado')], string="Estado", default='open')
    as_currency_id = fields.Many2one('res.currency', string="Currency")
    as_partner_id = fields.Many2one('res.partner', string="Contacto")
    as_user_id = fields.Many2one('res.users', string="Usuario", default=_default_user)
    as_date = fields.Date("Fecha", default=fields.Date.today)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analitíca', groups="analytic.group_analytic_accounting")
    as_inpayment_ids = fields.One2many('as.payment.multi', 'as_tesoreria_id', string='Lineas de Pago Ingreso', readonly=True, copy=True,domain=[('as_payment_type','=','inbound')])
    as_outpayment_ids = fields.One2many('as.payment.multi', 'as_tesoreria_id', string='Lineas de Pago Egreso', readonly=True, copy=True,domain=[('as_payment_type','=','outbound')])
    as_deposit_ids = fields.One2many('as.deposit.digest', 'as_tesoreria_id', string='Lineas depositos', readonly=True, copy=False)
    as_amount_total_ingreso = fields.Float('Total Ingreso',compute="_compute_payment_caja")
    as_caja_chica_ids = fields.One2many('as.caja.chica', 'as_tesoreria_id', string='Lineas de Pago Egreso', readonly=True, copy=True)
    as_account_gasto_id = fields.Many2one('account.account', string="Cuenta Caja Chica")
    as_saldo_inicial = fields.Float('Saldo inicial')
    as_account_id =  fields.Many2one('account.move', string='Asiento Contable')
    as_account_iva =  fields.Many2one('account.account', string='Cuenta IVA')
    journal_id = fields.Many2one('account.journal',  domain=[('type', '=', 'purchase')], string="Diario")
    as_es_fiscal = fields.Boolean(string="Es fiscal", default=False)
    as_tipo_referencia = fields.Char(string="Referencia")
    as_monto_total = fields.Float(string='Monto Total', store=True, readonly=True, compute="traer_monto")

    @api.depends('as_caja_chica_ids.state')
    def traer_monto(self):
        for tesoreria in self:
            amount_untaxed = 0
            lineas_caja = tesoreria.as_caja_chica_ids
            if lineas_caja:
                for line in lineas_caja:
                    if line.state != 'cancel':
                        amount_untaxed += line.as_amount
                tesoreria.update({
                    'as_monto_total': amount_untaxed,
                })
                
    def as_recalculate_amount_total(self):
        for tesoreria in self:
            amount_untaxed = 0
            lineas_caja = tesoreria.as_caja_chica_ids
            if lineas_caja:
                for line in lineas_caja:
                    if line.state != 'cancel':
                        amount_untaxed += line.as_amount
                tesoreria.update({
                    'as_monto_total': amount_untaxed,
                })
                
    def name_get(self):
        result = []
        for banco in self:
            name = banco.name+' - '+banco.as_user_id.name
            result.append((banco.id,name))
        return result

    @api.depends('as_inpayment_ids','as_deposit_ids')
    def _compute_payment_caja(self):
        amount_total = 0.0
        amount_deposit = 0.0
        for pago in self:
            for payment in self.as_inpayment_ids.filtered(lambda r: r.state != 'cancel'):
                if payment.payment_acquirer_id.tipo_documento == 0:
                    amount_total+=payment.as_amount
            for payment in self.as_deposit_ids.filtered(lambda r: r.state != 'cancel'):
                if payment.as_extract_efectivo:
                    amount_deposit+=payment.as_amount
            pago.as_amount_total_ingreso=amount_total-amount_deposit

    def as_get_caja_report_in_close(self):
        return self.env.ref('as_bo_tesoreria.as_bo_tesoreria_preliminar').report_action(self)
    
    def as_imprimir_pdf_caja_chica(self):
        return self.env.ref('as_bo_tesoreria.as_reporte_pdf_libro_caja_view').report_action(self)
    
    def as_imprimir_pdf_caja_chica_previa(self):
        return self.env.ref('as_bo_tesoreria.as_reporte_pdf_libro_caja_previa').report_action(self)
    #     moves = []
    #     for order in self:
    #         for line in order.as_caja_chica_ids:
    #             for inv in line.as_invoice_id.move_id.line_ids:
    #                 moves.append(inv.id)

    #         pay_records = self.env['account.move.line']
    #         pay_records |= self.env['account.move.line'].sudo().search([('move_id.state', '=', 'posted'),('id', '=', moves)])
    #         order.as_moves_count = len(pay_records.ids)

    # as_moves_count = fields.Integer(string='Payments', compute='_compute_payment')

    # def action_view_moves(self):
    #     moves = []
    #     for order in self:
    #         for line in order.as_caja_chica_ids:
    #             for inv in line.as_invoice_id.move_id.line_ids:
    #                 moves.append(inv.id)
    #         pay_records = self.env['account.move.line']
    #         pay_records |= self.env['account.move.line'].sudo().search([('move_id.state', '=', 'posted'),('id', '=', moves)])
    #     return {
    #         'name': _('Apuntes Contables'),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move.line',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('id', 'in', pay_records.ids)],
    #     }


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.tesoereria') or _('New')
        result = super(AsTesoreria, self).create(vals)
        return result


    def add_payment(self):
        context = dict(self.env.context or {})
        as_type_saldo = str(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_modalidad'))
        context['default_as_payment_type'] = self._context['default_as_payment_type']
        context['default_as_tesoreria_id'] = self.id
        if as_type_saldo == 'Factura':
            context['default_as_type'] = 'invoice'
        elif as_type_saldo == 'Venta':
            context['default_as_type'] = 'sale'
        action = {
            'name': _('Pago de Clientes'),
            'view_mode': 'form',
            'res_model': 'as.payment.multi',
            'view_id': self.env.ref('as_bo_tesoreria.as_payment_multi_form_p').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        return action    
    
    def add_payment_deposit(self):
        context = dict(self.env.context or {})
        context['default_as_tesoreria_id'] = self.id
        action = {
            'name': _('Depositos'),
            'view_mode': 'form',
            'res_model': 'as.deposit.digest',
            'view_id': self.env.ref('as_bo_tesoreria.view_deposit_digest_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        return action


    def add_payment_caja(self):
        return {
            'context' : {
                'default_as_tesoreria_id' : self.id,
                'default_account_analytic_id' : self.account_analytic_id.id,
                },
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'as.caja.chica',
            'view_id' : False,
            'type' : 'ir.actions.act_window',
            'target' : 'new',
        }


    @api.onchange('as_account_gasto_id','as_partner_id')
    def as_control_saldo_account(self):
        account_id = self.as_account_gasto_id
        partner_id = self.as_partner_id
        total = 0.0
        asientos = []
        resultado = 0.0
        if self.as_account_gasto_id and partner_id:
            account_query = ("""
                SELECT debit,credit,am.id from account_move_line aml 
                join account_move am on am.id = aml.move_id
                where am.state='posted' and aml.account_id= """ +str(account_id.id)+ """ and aml.partner_id= """ +str(partner_id.id)+ """ order by am.date asc """)
            self.env.cr.execute(account_query)
            total = 0.0
            for move_line in self.env.cr.fetchall():
                asientos.append(move_line[2])
                resultado = float(move_line[0])-float(move_line[1])
                total += resultado
        self.as_saldo_inicial = total

    def as_get_caja_close(self):
        a=0
        move_create = self.env['account.move']
        move = self.env['account.move']
        for line_deposit in self.as_deposit_ids:
            if line_deposit.state == 'draft':
                line_deposit.state = 'confirm'
                for line_check in line_deposit.as_checks_ids:
                    line_check.state = 'collected'

        if not self.as_account_iva:
            raise UserError(_("Debe completar la cuenta IVA!"))
        if not self.as_account_gasto_id:
            raise UserError(_("Debe seleccionar la cuenta de caja chica!"))
        if self.as_account_iva and self.as_account_gasto_id:
            account_out = self.as_account_gasto_id.id
            account_iva = self.as_account_iva.id
            if not self.as_account_id:
                if len(self.as_caja_chica_ids)>0:
                    move_vals = {
                        'journal_id': self.journal_id.id,
                        'date': self.as_date,
                        'ref': 'Asiento de caja '+str(self.display_name),
                        'line_ids': [],
                        
                    }
                    move = move_create.create(move_vals)
                    self._create_account_move_line_caja(move) 
                self.as_account_id = move
            else:
                self._create_account_move_line_caja(self.as_account_id) 
            if self.as_account_id.state == 'draft':
                self.as_account_id.post()
        for line in self.as_caja_chica_ids:
            if line.as_invoice_id and line.as_invoice_id.state == 'posted':
                line.write({'state':'confirm'})
            else:
                line.write({'state':'cancel'})

        self.state = 'close'

    def as_get_caja_open(self):
        if self.state != 'cancel':
            self.state = 'open'
            for line in self.as_caja_chica_ids:
                if line.as_invoice_id and line.as_invoice_id.state == 'posted':
                    line.write({'state':'new'})
                else:
                    line.write({'state':'cancel'})
            self.as_account_id.button_draft()
            self.as_account_id.line_ids.unlink()

    def _create_account_move_line_caja(self,move_generate):
        line_move = self.env['account.move.line']
        monto_credit = 0.0
        as_account_id = self.as_account_gasto_id
        partner_search = self.as_user_id.partner_id
        for line in self.as_caja_chica_ids:
            if line.as_invoice_id and line.as_invoice_id.state == 'posted':
                for move in line.as_invoice_id.line_ids:
                    if move.account_id != move.move_id.partner_id.property_account_payable_id and move.account_id != as_account_id:
                        line_move |= move.with_context(move_id = move_generate.id,check_move_validity=False).copy({
                            'move_id': move_generate.id,
                        })
                    elif move.account_id == move.move_id.partner_id.property_account_payable_id and move.debit > 0:
                        line_move |= move.with_context(move_id = move_generate.id,check_move_validity=False).copy({
                            'move_id': move_generate.id,
                        })
                    elif move.account_id == as_account_id and move.debit > 0:
                        line_move |= move.with_context(move_id = move_generate.id,check_move_validity=False).copy({
                            'move_id': move_generate.id,
                        })
                    else:
                        monto_credit += move.credit
                # for line_m in line_move:
                #     if not line.as_invoice_id.as_tipo_factura.as_seg_anticipado:
                #         if line_m.account_id == line.as_invoice_id.partner_id.property_account_payable_id:
                #             as_account_id = self.as_account_gasto_id.id
                #             line_m.partner_id = self.as_partner_id
                #             self.env.cr.execute('UPDATE account_move_line SET  account_id='+str(as_account_id)+' WHERE id='+str(line_m.id))
        if monto_credit > 0.0:
            res = {
                'move_id': move_generate.id,
                'name': move_generate.name+' '+self.name,
                'partner_id': partner_search.id,
                'analytic_account_id': self.account_analytic_id.id,
                'account_id': as_account_id.id,
                'debit': 0.0,
                'credit': monto_credit,
                'amount_currency': monto_credit,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            line_move |= self.env['account.move.line'].with_context(check_move_validity=False).create(res)


        return line_move
    
