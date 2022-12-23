# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, SU, SA
_logger = logging.getLogger(__name__)


class AsPaymentMulti(models.Model):
    _name = 'as.payment.multi'

    
    @api.onchange('journal_id')
    def _change_product_partner(self):
        domain = []
        if self.journal_id.as_anticipo:
            self.as_type = 'anticipo'
        # if self.as_payment_type == 'inbound':
        #     domain = [('customer_rank', '>', 0)]
        # else:
        #     domain =  [('supplier_rank', '>', 0)]
        self.get_anticipos_cliente()
        return {'domain': {'as_partner_id':domain }}

    @api.onchange('as_payment_type')
    def _change_product_journal(self):
        domain = []
        if self.as_payment_type == 'inbound':
            domain = [('as_type_journal', '=', 'inbound')]
        else:
            domain = [('as_type_journal', '=', 'outbound')]

        return {'domain': {'journal_id':domain }}

    name = fields.Char('Titulo')
    as_payment_type = fields.Selection([('inbound', 'Ingreso'), ('outbound', 'Egreso')], string="Tipo de Pago",required=True)
    as_partner_id = fields.Many2one('res.partner', string="Cliente/Empresa")
    journal_id = fields.Many2one('account.journal', string="Diario",domain=_change_product_journal)
    payment_acquirer_id = fields.Many2one('as.payment.acquirer', string='Método de Pago',required=True)
    as_is_anticipo = fields.Boolean('Pago con Anticipo',related="payment_acquirer_id.as_is_anticipo")
    as_numero_documento = fields.Char('Nro documento', help=u'Número del documento del banco.')
    as_recibo_manual = fields.Char('Nro documento', help=u'Número del documento del banco.')
    as_metodo_pago_bolean = fields.Integer(related='payment_acquirer_id.tipo_documento', string="Boolean")
    as_is_credito = fields.Boolean(related='payment_acquirer_id.as_is_credito', string="Credito")
    as_is_debit = fields.Boolean(related='payment_acquirer_id.as_is_debit', string="debito")
    as_cuotas = fields.Integer('Cuotas')
    as_code_authorization = fields.Char('codigo de Autorización')
    as_bank_id = fields.Many2one('res.partner.bank', string="Banco",domain="[('partner_id','=', as_partner_id)]")
    as_amount = fields.Float('Monto a Pagar')
    as_amounta = fields.Float('Saldo Anticipo')
    as_amount_anticipo = fields.Float('Saldo Anticipo Acumulado')
    date = fields.Datetime(string='Fecha de pago', default=lambda self: fields.Datetime.now())
    as_sale_ids = fields.Many2many('as.payment.multi.line',string="Ventas")
    currency_id = fields.Many2one('res.currency', string="Divisa")
    as_nota = fields.Char('Comentario')
    state = fields.Selection([('cancel', 'Cancelado'),('new', 'Nuevo'), ('data', 'Ventas'),('confirm', 'Procesado')], string='Status', required=True, readonly=True, copy=False, default='new')
    payment_ids = fields.Many2many('as.sale.payment.line', string='Anticipos registrados')
    as_tesoreria_id = fields.Many2one('as.tesoreria',string="Caja de Tesoreria")
    as_type= fields.Selection([('sale', 'Ventas'), ('invoice', 'Facturas'),('anticipo', 'Anticipo'),('prestamos', 'Prestamos'),('quincena', 'Aguinaldo'),('Desembolso', 'Desembolso'),('Diferencia', 'Diferencia'),('quiquenio', 'Anticipo Quinquenio'),('individual','Anticipo Individual'),('dividendo', 'Anticipo Dividendos'),('multi_pago', 'Multipago Quincena'),('asiento_asjuste', 'Asiento Ajuste'),('finiquito', 'Liquidación o Indemnización'),('Otros', 'Otros')], string="Tipo Documento", required=True)
    account_move_id = fields.Many2one('account.move', string="Pago Generado")
    as_amount_line = fields.Boolean('Calculo en Lineas',default=False)
    as_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica')
    as_account_debit = fields.Many2one('account.account', string='Cuenta Debe')
    as_account_credit = fields.Many2one('account.account', string='Cuenta Haber')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.operacion') or _('New')
        result = super(AsPaymentMulti, self).create(vals)
        result.get_sale_process()
        return result

    
    def cancel_payment(self):
        self.state='cancel'
        for line in self.as_sale_ids:
            line.state = 'cancelled'
            if line.account_move_id:
                line.account_move_id.button_cancel()   
                for line_move in line.account_move_id.line_ids:
                    self.env['account.move.line'].browse(line_move.id).remove_move_reconcile()
            if line.account_movea_id:
                line.account_movea_id.button_cancel()   
                for line_move in _move.account_movea_id.line_ids:
                    self.env['account.move.line'].browse(line_move.id).remove_move_reconcile()
            if line.as_sale_id:
                line.as_sale_id.ajustar_saldos(False)
            if line.as_invoice_id:
                sale = self.env['sale.order'].search([('name','=', line.as_invoice_id.invoice_origin)],limit=1)
                if sale:
                    sale.ajustar_saldos(False)
    
    def get_sale_draft(self):
        self.state='new'

    @api.onchange('as_sale_ids')
    def get_payment_line_ids(self):  
        self.as_amount = 0.0
        for sale in self.as_sale_ids:
            self.as_amount += sale.as_amount
            total = 0.0
            # if self.as_is_anticipo:
            #     self.as_amount = 0.0
                # for payment in self.payment_ids:
                #     if payment.is_pago:
                #         currency = self.currency_id
                #         self.as_amount += self.env.user.currency_id._convert(abs(payment.amount_to_pay), currency, self.env.user, self.date)
            # if sale.as_amount > sale.as_amount_total:
            #     raise UserError(_("Excede la cantidad de la venta!"))


    # @api.onchange('payment_ids')
    # def get_payment_ids(self):  
    #     for payment in self.payment_ids:
    #         if payment.is_pago:
    #             self.as_amount = 0.0
    #             self.as_amounta = 0.0
    #             currency = self.currency_id
    #             amount_to_show = self.env.user.currency_id._convert(abs(payment.amount_to_pay), currency, self.env.user, self.date)
    #             self.as_amount += amount_to_show
    #             self.as_amounta += amount_to_show

    @api.onchange('as_amount')
    def get_as_amount(self):  
        cont = 0
        facturas = ''
        total = self.as_amount
        if self.as_type not in ('anticipo','quincena','prestamos','Desembolso','Diferencia','quiquenio','individual','dividendo','multi_pago','asiento_asjuste','finiquito','Otros') and not self.as_amount_line:
            if self.as_amount != 0.0:
                for datos in self:
                    fecha_str =  (datetime.strptime(str(self.date), '%Y-%m-%d %H:%M:%S')).strftime('%d-%m-%Y')
                    amount_total = 0.00
                    for linet in datos.as_sale_ids:
                        amount_total += linet.as_amount_total
                    if datos.as_amount > amount_total:
                        datos.as_amount = amount_total
                    currency_default = datos.env.user.company_id.currency_id
                    currency_trans = datos.as_partner_id.currency_id
                    monto = self._conertir_moneda(currency_default,currency_trans,datos.as_amount,datos.date)
                    for line in datos.as_sale_ids:
                        moneda = datos.currency_id.name
                        line.currency_id = datos.currency_id
                        if monto >= line.as_amount_total:
                            line.as_amount = line.as_amount_total
                            monto -= round(line.as_amount_total,2)
                        elif monto > 0:
                            line.as_amount = round(monto,2)
                            monto = 0
                        else: line.as_amount = 0.0
                    for linet in datos.as_sale_ids:
                        if linet.as_amount > 0:
                            if datos.as_type == 'invoice':
                                if datos.as_payment_type == 'inbound' and 'as_invoice_number' in linet.as_invoice_id._fields:
                                    facturas += str(linet.as_invoice_id.as_invoice_number)+','
                                else:
                                    facturas += linet.as_invoice_id.name+','

                            else:
                                facturas += linet.as_sale_id.name+','
                    datos.as_nota = str(fecha_str)+' '+str(facturas)+' '+str(self.as_partner_id.name)+' Pago en '+str(self.payment_acquirer_id.name)
            cont = len(self.as_sale_ids)
            # if cont > 0 and total > 0 and not self.as_is_anticipo:
            #     diferencia = total - self.as_amount
            #     self.as_amount = total
            #     self.as_sale_ids[cont-1].as_amount= self.as_sale_ids[cont-1].as_amount + round(diferencia,2)

    @api.onchange('as_partner_id','journal_id','payment_acquirer_id','date')
    def get_as_note(self):  
        for registro in self:
            facturas = ''
            # fecha_str =  (datetime.strptime(str(self.date), '%Y-%m-%d %H:%M:%S')).strftime('%d-%m-%Y')
            fecha_str = (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)).strftime('%d-%m-%Y')
            for linet in registro.as_sale_ids:
                if linet.as_amount > 0:
                    if registro.as_type == 'invoice':
                        if registro.as_payment_type == 'inbound' and  'as_invoice_number' in linet.as_invoice_id._fields:
                            facturas += str(linet.as_invoice_id.as_invoice_number)+','
                        else:
                            facturas += linet.as_invoice_id.name+','
                    else:
                        facturas += linet.as_sale_id.name+','
            registro.as_nota = str(fecha_str)+' '+str(facturas)+' '+str(registro.as_partner_id.name)+' '+str(registro.payment_acquirer_id.name)

    @api.onchange('as_partner_id','journal_id','as_type')
    def get_as_partner_id(self):  
        for registro in self:
            if registro.as_partner_id:
                if registro.as_payment_type == 'inbound':
                    account_anticipo_id = registro.as_partner_id.property_account_anticipo_id
                    registro.as_amount_anticipo = (registro.as_control_saldo_partner(account_anticipo_id,registro.as_partner_id)[0])*-1   
                else:
                    account_anticipo_id = registro.as_partner_id.property_account_supplier_id
                    registro.as_amount_anticipo = (registro.as_control_saldo_partner(account_anticipo_id,registro.as_partner_id)[0])  
            if self.as_is_anticipo:
                self.get_anticipos_cliente()
            if registro.as_type == 'sale':
                self.get_sales_deuda_ventas()
            elif registro.as_type == 'invoice':
                self.get_sales_deuda_invoice()

    def get_anticipos_cliente(self):   
        if self.journal_id.as_is_pago_anticipo:
            self.as_amount = 0.0    
            pagos = []
            pago = self.env['as.payment.acquirer'].search([('as_is_anticipo','=', True)],limit=1)
            if not pago:
                raise UserError(_("Debe tener habilitado un metodo de pago contra anticipo!"))
            else:
                self.payment_acquirer_id = pago
            if self.as_partner_id and self.as_is_anticipo:
                if self.as_payment_type == 'inbound':
                    self.as_amounta = self.as_partner_id.as_anticipo_count
                    account_anticipo_id = self.as_partner_id.property_account_anticipo_id
                else:
                    self.as_amounta = self.as_partner_id.as_anticipo_supplier_count
                    account_anticipo_id = self.as_partner_id.property_account_supplier_id

                saldo_anticipo = self.as_control_saldo_partner(account_anticipo_id,self.as_partner_id)     
                # if saldo_anticipo:        
                #     if self.as_payment_type == 'inbound':
                #         monto =  saldo_anticipo[0]*-1
                #     else:
                #         monto =  saldo_anticipo[0]

                #     vals = {
                #         'currency_id': self.env.user.currency_id.id,
                #         'amount_to_pay': monto,
                #         'move_line_id': saldo_anticipo[1],
                #     }
                #     pagos.append(vals)
                #     payments=self.env['as.sale.payment.line'].sudo().create(pagos)
                #     self.payment_ids.unlink()
                #     self.payment_ids = payments.ids

    def as_control_saldo_partner(self,account_id,partner):
        total = 0.0
        asientos = []
        resultado = 0.0
        if not account_id:
            raise UserError(_("Cuenta de anticipo de Cliente/Empresa vacio!"))
        account_query = ("""
            SELECT debit,credit,am.id from account_move_line aml 
            join account_move am on am.id = aml.move_id
            where am.state='posted' and aml.partner_id = """ +str(partner.id)+ """ and aml.account_id= """ +str(account_id.id)+ """ order by am.date asc """)
        self.env.cr.execute(account_query)
        total = 0.0
        for move_line in self.env.cr.fetchall():
            asientos.append(move_line[2])
            resultado = float(move_line[0])-float(move_line[1])
            total += resultado
        return total,asientos

    def get_sales_deuda_ventas(self):
        sales_ids = []
        cont = 0
        total = self.as_amount
        self.as_sale_ids.unlink()
        # if self.as_amount <= 0:
        #     raise UserError(_("Amount can't be negative or zero !"))
        if self.as_partner_id.id:
            consulta = "SELECT\
                            ai.id,ai.as_saldo,ai.name,ai.name,to_char(ai.date_order, 'YYYY-MM-DD'),pp.currency_id\
                            FROM sale_order AS ai\
                            join product_pricelist AS pp on pp.id=ai.pricelist_id\
                            WHERE ai.as_saldo > 1.5 and invoice_status = 'to invoice'\
                            AND ai.state not in ('draft','cancel') and ai.partner_id = %s order by ai.date_order asc"
            self.env.cr.execute(consulta,[(self.as_partner_id.id)])
            amount = self.as_amount
            for invoice in self.env.cr.fetchall():
                currency_sale = self.env['res.currency'].search([('id','=', invoice[5])])
                amount_total = currency_sale._convert(invoice[1],self.currency_id,self.env.user.company_id, self.date,round=False)
                if amount > 0:
                    if float(amount_total) >= float(amount):
                        amount = float(amount_total)
                    else:
                        amount = amount - float(amount_total)
                vals = { 
                    'name':invoice[3],
                    'date':invoice[4],
                    'as_sale_id' : invoice[0],
                    'as_amount_total' : amount_total,
                }
                line_id = self.env['as.payment.multi.line'].create(vals)
                sales_ids.append(line_id.id)
                cont+=1
            self.as_sale_ids = sales_ids
            if self.as_amount != 0.0:
                for datos in self:
                    amount_total = 0.00
                    for linet in datos.as_sale_ids:
                        amount_total += linet.as_amount_total
                    if datos.as_amount > amount_total:
                        datos.as_amount = amount_total
                    currency_default = datos.env.user.company_id.currency_id
                    currency_trans = datos.as_partner_id.currency_id
                    monto = self._conertir_moneda(currency_default,currency_trans,datos.as_amount,datos.date)
                    for line in datos.as_sale_ids:
                        moneda = datos.currency_id.name
                        line.currency_id = datos.currency_id
                        if monto >= line.as_amount_total:
                            line.as_amount = line.as_amount_total
                            monto -= round(line.as_amount_total,2)
                        elif monto > 0:
                            line.as_amount = round(monto,2)
                            monto = 0
                        else: line.as_amount = 0.0
            # if cont > 0 and total > 0 and not self.as_is_anticipo:
            #     diferencia = total - self.as_amount
            #     self.as_amount = total
            #     self.as_sale_ids[cont-1].as_amount= self.as_sale_ids[cont-1].as_amount + round(diferencia,2)
        self.state = 'data'

    def get_sales_deuda_invoice(self):
        sales_ids = []
        cont = 0
        total = self.as_amount
        self.as_sale_ids.unlink()
        # if self.as_amount <= 0:
        #     raise UserError(_("Amount can't be negative or zero !"))
        if self.as_partner_id.id:
            consulta = "SELECT\
                            ai.id,ai.amount_residual,ai.name,name,to_char(ai.invoice_date, 'YYYY-MM-DD'),ai.currency_id\
                            FROM account_move AS ai\
                            WHERE ai.amount_residual > 0\
                            AND ai.state not in ('draft','cancel') and ai.partner_id = %s and (as_is_gasto = False or as_is_gasto is null) order by ai.invoice_date asc"
            self.env.cr.execute(consulta,[(self.as_partner_id.id)]) 
            amount = self.as_amount
            for invoice in self.env.cr.fetchall():
                currency_sale = self.env['res.currency'].search([('id','=', invoice[5])])
                amount_total = currency_sale._convert(invoice[1],self.currency_id,self.env.user.company_id, self.date,round=False)
                if amount > 0:
                    if float(amount_total) >= float(amount):
                        amount = float(amount_total)
                    else:
                        amount = amount - float(amount_total)
                line_invoice = self.env['account.move.line'].search([('move_id','=',invoice[0]),('exclude_from_invoice_tab', '=', False)],limit=1)
                vals = { 
                    'name':invoice[3],
                    'date':invoice[4],
                    'as_invoice_id' : invoice[0],
                    'as_analytic_account_id' : line_invoice.analytic_account_id.id,
                    'as_amount_total' : amount_total,
                }
                line_id = self.env['as.payment.multi.line'].create(vals)
                sales_ids.append(line_id.id)
                cont+=1
            self.as_sale_ids = sales_ids
            if self.as_amount != 0.0:
                for datos in self:
                    amount_total = 0.00
                    for linet in datos.as_sale_ids:
                        amount_total += linet.as_amount_total
                    if datos.as_amount > amount_total:
                        datos.as_amount = amount_total
                    currency_default = datos.env.user.company_id.currency_id
                    currency_trans = datos.as_partner_id.currency_id
                    monto = self._conertir_moneda(currency_default,currency_trans,datos.as_amount,datos.date)
                    for line in datos.as_sale_ids:
                        moneda = datos.currency_id.name
                        line.currency_id = datos.currency_id
                        if monto >= line.as_amount_total:
                            line.as_amount = line.as_amount_total
                            monto -= round(line.as_amount_total,2)
                        elif monto > 0:
                            line.as_amount = round(monto,2)
                            monto = 0
                        else: line.as_amount = 0.0
            if cont > 0 and total > 0 and not self.as_is_anticipo:
                diferencia = total - self.as_amount
                self.as_amount = total
                self.as_sale_ids[cont-1].as_amount= self.as_sale_ids[cont-1].as_amount + round(diferencia,2)
        self.state = 'data'

    def _conertir_moneda(self,currency_trans,currency_default,amount,date):
        if currency_default != currency_trans:
            return currency_trans._convert(self.amount,currency_default,self.company_id, self.date,round=False)
        else:
            return round(amount,2)

    @api.onchange('journal_id')
    def get_currency_journal(self):
        if not self.journal_id.currency_id:
            self.currency_id = self.env.user.company_id.currency_id
        else:
            self.currency_id = self.journal_id.currency_id

    def _create_accounting_entries_sale(self,account_in,account_out):

        debit_account_id = account_in

        already_out_account_id = False
        credit_account_id = account_out
        if self.as_payment_type == 'inbound' and self.as_type == 'sale':
            return self._create_account_move_line_sale(credit_account_id, debit_account_id)
        else:
            return self._create_account_move_line_invoice(credit_account_id, debit_account_id)
    
    def _create_account_move_line_sale(self, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        AccountMoveLine = []
        total_credit = 0.0
        amount = 0.0
        base_line = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
            # 'analytic_account_id': self.as_partner_id.account_analytic_id.id,
        }
        amount_access = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_amount_access'))
        credit_diferencia = self.journal_id.profit_account_id.id
        credit_anticipo = self.as_partner_id.property_account_anticipo_id.id
        currency_id = self.currency_id
        amount_haber = 0.0
        credit_line = {}
        parcial = False
        for line in self.as_sale_ids:
            monto = 0.0
            mont2 = 0.0
            if line.state == 'draft':
                if line.as_amount > 0.0:
                    currency_id = self.currency_id
                    line.state = 'posted'
                    if line.as_amount < line.as_amount_total:
                        monto = line.as_amount
                        monto2 = line.as_amount_total
                        parcial = True
                    else:
                        monto = round(line.as_amount,2)
                        monto2 = line.as_amount
                    amount += currency_id._convert((monto2),line.as_sale_id.company_id.currency_id, line.as_sale_id.company_id, line.as_sale_id.date_order,round=True)
                    amount_pagar = currency_id._convert((monto),line.as_sale_id.company_id.currency_id, line.as_sale_id.company_id, line.as_sale_id.date_order,round=True)
                    credit_line = dict(base_line, account_id=credit_account_id,debit=0.00,credit=amount_pagar,sale_id=line.as_sale_id.id)
                    AccountMoveLine.append([0, 0, credit_line])
                    total_credit += amount_pagar
        currency_difs = total_credit-amount
        currency_dif = abs( total_credit-amount)
        if currency_dif <= amount_access and currency_dif >= (amount_access*-1):
            if currency_dif >= 0.01 or currency_dif <= -0.01:
                credit_line = self._create_accounting_dif(credit_diferencia,currency_dif,currency_difs,base_line,line.as_sale_id.id,False)
                AccountMoveLine.append([0, 0, credit_line])
                total_credit += currency_dif
        elif currency_difs < amount_access and parcial != True:
            credit_line = dict(base_line, account_id=credit_anticipo,debit=0.00,credit=currency_dif,sale_id=line.as_sale_id.id)
            AccountMoveLine.append([0, 0, credit_line])                    
            total_credit += currency_dif


        debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
        AccountMoveLine.append([0, 0, debit_line])

        return AccountMoveLine
        
    def _create_accounting_dif(self, account_out, qty_out,diferencia,base_line,sale,invoice):
        sale_id = sale
        account_id = account_out
        lines = []
        move_line = {}
        if self.as_payment_type == 'outbound':
            if diferencia > 0:
                account_id = self.journal_id.as_account_eg_positiva.id
                move_line = dict(base_line, account_id=account_id,debit=0.00,credit=qty_out,sale_id=sale,invoice_id=invoice)
            else:
                account_id = self.journal_id.as_account_eg_negativo.id
                move_line = dict(base_line, account_id=account_id,debit=qty_out,credit=0.00,sale_id=sale,invoice_id=invoice)
        else:
            if diferencia > 0:
                account_id = self.journal_id.as_account_in_positivo.id
                move_line = dict(base_line, account_id=account_id,debit=qty_out,credit=0.00,sale_id=sale,invoice_id=invoice)
            else:
                account_id = self.journal_id.as_account_in_negativo.id
                move_line = dict(base_line, account_id=account_id,debit=0.00,credit=qty_out,sale_id=sale,invoice_id=invoice)

        return move_line

    def _create_accounting_entries_anticipo(self, credit_account_id, debit_account_id):
        AccountMoveLine = []
        total_credit = 0.0
        #no tocar los partner de estos diccionarios o alteraran el saldo de anticipo
        base_line = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
        }
        base_line_b = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
        }
        currency_id = self.journal_id.currency_id
        total_credit = currency_id._convert((self.as_amount),self.env.user.company_id.currency_id, self.env.user.company_id, self.date,round=True)
        debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
        AccountMoveLine.append([0, 0, debit_line])
        credit_line = dict(base_line_b, account_id=credit_account_id,debit=0.00,credit=total_credit)
        AccountMoveLine.append([0, 0, credit_line])
        if self.journal_id.currency_id.id == 2:
            base_line2 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_partner_id.id,
            }
            base_line3 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_tesoreria_id.as_user_id.partner_id.id,
            }
            total_credit2 = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_itf_catidad'))
            debit_line2 = dict(base_line2, account_id=self.journal_id.as_itf.id,debit=total_credit2*total_credit,credit=0.00)
            AccountMoveLine.append([0, 0, debit_line2])
            credit_line2 = dict(base_line3, account_id=self.journal_id.payment_debit_account_id.id,debit=0.00,credit=total_credit2*total_credit)
            AccountMoveLine.append([0, 0, credit_line2])
        return AccountMoveLine
    
    def _create_accounting_entries_rembolse(self, credit_account_id, debit_account_id):
        AccountMoveLine = []
        total_credit = 0.0
        #no tocar los partner de estos diccionarios o alteraran el saldo de anticipo
        
        base_line = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
        }
        base_line_b = {
            'name': self.as_nota,
            'partner_id': self.env.user.partner_id.id,
        }
        currency_id = self.journal_id.currency_id
        total_credit = currency_id._convert((self.as_amount),self.env.user.company_id.currency_id, self.env.user.company_id, self.date,round=True)
        debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
        AccountMoveLine.append([0, 0, debit_line])
        credit_line = dict(base_line_b, account_id=credit_account_id,debit=0.00,credit=total_credit)
        AccountMoveLine.append([0, 0, credit_line])
        if self.journal_id.currency_id.id == 2:
            base_line2 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_partner_id.id,
            }
            base_line3 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.env.user.partner_id.id,
            }
            total_credit2 = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_itf_catidad'))
            debit_line2 = dict(base_line2, account_id=self.journal_id.as_itf.id,debit=total_credit2*total_credit,credit=0.00)
            AccountMoveLine.append([0, 0, debit_line2])
            credit_line2 = dict(base_line3, account_id=self.journal_id.payment_debit_account_id.id,debit=0.00,credit=total_credit2*total_credit)
            AccountMoveLine.append([0, 0, credit_line2])
        return AccountMoveLine

    def _create_accounting_entries_quinquenio(self, credit_account_id, debit_account_id):
        AccountMoveLine = []
        total_credit = 0.0
        #no tocar los partner de estos diccionarios o alteraran el saldo de anticipo
        base_line = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
        }
        base_line_b = {
            'name': self.as_nota,
            'partner_id': self.env.user.partner_id.id,
        }
        currency_id = self.journal_id.currency_id
        total_credit = currency_id._convert((self.as_amount),self.env.user.company_id.currency_id, self.env.user.company_id, self.date,round=True)
        debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
        AccountMoveLine.append([0, 0, debit_line])
        credit_line = dict(base_line_b, account_id=credit_account_id,debit=0.00,credit=total_credit)
        AccountMoveLine.append([0, 0, credit_line])
        if self.journal_id.currency_id.id == 2:
            base_line2 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_partner_id.id,
            }
            base_line3 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_tesoreria_id.as_user_id.partner_id.id,
            }
            total_credit2 = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_itf_catidad'))
            debit_line2 = dict(base_line2, account_id=self.journal_id.as_itf.id,debit=total_credit2*total_credit,credit=0.00)
            AccountMoveLine.append([0, 0, debit_line2])
            credit_line2 = dict(base_line3, account_id=self.journal_id.payment_debit_account_id.id,debit=0.00,credit=total_credit2*total_credit)
            AccountMoveLine.append([0, 0, credit_line2])
        return AccountMoveLine

    def _create_accounting_entries_diferencia(self, credit_account_id, debit_account_id):
        AccountMoveLine = []
        total_credit = 0.0

        base_line = {
            'name': self.as_nota,
            'partner_id': self.as_tesoreria_id.as_user_id.partner_id.id,
        }
        base_line_b = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
        }
        currency_id = self.journal_id.currency_id
        total_credit = currency_id._convert((self.as_amount),self.env.user.company_id.currency_id, self.env.user.company_id, self.date,round=True)
        debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
        AccountMoveLine.append([0, 0, debit_line])
        credit_line = dict(base_line_b, account_id=credit_account_id,debit=0.00,credit=total_credit)
        AccountMoveLine.append([0, 0, credit_line])
        if self.journal_id.currency_id.id == 2:
            base_line2 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_partner_id.id,
            }
            base_line3 = {
            'name': 'ITF'+' '+str(self.as_nota),
            'partner_id': self.as_tesoreria_id.as_user_id.partner_id.id,
            }
            total_credit2 = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_itf_catidad'))
            debit_line2 = dict(base_line2, account_id=self.journal_id.as_itf.id,debit=total_credit2*total_credit,credit=0.00)
            AccountMoveLine.append([0, 0, debit_line2])
            credit_line2 = dict(base_line3, account_id=self.journal_id.payment_debit_account_id.id,debit=0.00,credit=total_credit2*total_credit)
            AccountMoveLine.append([0, 0, credit_line2])
        return AccountMoveLine


    def get_date_vencimiento(self,date):
        date = date - relativedelta(hours=4)
        start_date = date
        end_date = date + relativedelta(days=7)
        hora_start = datetime.strptime('14:00', '%H:%M')
        hora_end = datetime.strptime('00:01', '%H:%M')
        hora_pago = datetime.strptime(str(date.hour)+':'+str(date.minute), '%H:%M')
        fechas = []
        day_count = (end_date - start_date).days + 1
        for single_date in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:
            if single_date.isoweekday() not in [5,6]:
                fechas.append(single_date)
        if hora_pago >= hora_start and hora_pago <=  hora_end:
            fecha_def = fechas[2] + relativedelta(hours=24)
        else:
            fecha_def = fechas[2] 

        return fecha_def.strftime('%Y-%m-%d')


    def _create_account_move_line_invoice(self, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        AccountMoveLine = []
        total_credit = 0.0
        amount = 0.0
        base_line = {
            'name': self.as_nota,
            'partner_id': self.as_partner_id.id,
            # 'analytic_account_id': self.as_partner_id.account_analytic_id.id,
        }
        base_line2 = {
            'name': self.as_nota,
            'partner_id': self.env.user.partner_id.id,
            # 'analytic_account_id': self.as_partner_id.account_analytic_id.id,
        }
        amount_access = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_amount_access'))
        credit_diferencia = self.journal_id.profit_account_id.id
        credit_anticipo = self.as_partner_id.property_account_anticipo_id.id
        currency_id = self.currency_id
        amount_haber = 0.0
        credit_line = {}
        parcial = False
        if self.payment_acquirer_id.as_is_credito or self.payment_acquirer_id.as_is_debit:
            credit_account_id = self.as_partner_id.property_account_receivable_id.id
            debit_account_id = self.journal_id.payment_debit_account_id.id
            debit_account_pagar_id = self.as_partner_id.property_account_payable_id.id
            total_pagar = 0.0
            total_cuota = 0.0
            total_credito = 0.0
            total_transbank = 0.0
            total_pagar = 0.0
            facturas = ''
            for line in self.as_sale_ids:
                total_pagar += currency_id._convert(line.as_amount,line.as_invoice_id.company_id.currency_id, line.as_invoice_id.company_id, line.as_invoice_id.invoice_date,round=True)
                facturas = line.as_invoice_id.name+','
            if self.as_cuotas <=0:
                raise UserError(_("El numero de cuotas no puede ser cero!"))
            total_cuota = total_pagar/self.as_cuotas  
            date_vencimiento= self.get_date_vencimiento(self.date)

            for i in range(0,self.as_cuotas):
                fecha_str =  (datetime.strptime(date_vencimiento, '%Y-%m-%d')).strftime('%d-%m-%Y')
                base_line['name'] = str(fecha_str)+'/'+str(i+1)+'/'+str(self.payment_acquirer_id.name)+'/'+str(self.as_code_authorization)+'/'+str(facturas)+'/'+str(self.as_partner_id.name)
                total_pagar = round(total_cuota*(self.payment_acquirer_id.as_porcentaje/100))+round(round(total_cuota*(self.payment_acquirer_id.as_porcentaje/100))*0.19)
                credit_line = dict(base_line, account_id=debit_account_pagar_id,debit=total_pagar,date_maturity=date_vencimiento,credit=0.0,invoice_id=line.as_invoice_id.id)
                AccountMoveLine.append([0, 0, credit_line])                
                total_transbank = round(total_cuota-total_pagar) 
                credit_line = dict(base_line, account_id=debit_account_id,debit=total_transbank,date_maturity=date_vencimiento,credit=0.0,invoice_id=line.as_invoice_id.id)
                AccountMoveLine.append([0, 0, credit_line])
                total_credito += total_pagar+total_transbank
                date_vencimiento = (datetime.strptime(date_vencimiento, '%Y-%m-%d') + relativedelta(days=30)).strftime('%Y-%m-%d')
            debit_line = dict(base_line, account_id=credit_account_id,debit=0.0,credit=total_credito,invoice_id=line.as_invoice_id.id)
            AccountMoveLine.append([0, 0, debit_line])


        elif self.as_is_anticipo:
            for line in self.as_sale_ids:
                monto = 0.0
                mont2 = 0.0
                if line.state == 'draft':
                    if line.as_amount > 0.0:
                        currency_id = self.currency_id
                        line.state = 'posted'
                        if line.as_amount < line.as_amount_total:
                            monto = line.as_amount
                            monto2 = line.as_amount_total
                            parcial = True
                        else:
                            monto = round(line.as_amount,2)
                            monto2 = line.as_amount
                        amount += currency_id._convert((monto2),line.as_invoice_id.company_id.currency_id, line.as_invoice_id.company_id, line.as_invoice_id.invoice_date,round=True)
                        amount_pagar = currency_id._convert((monto),line.as_invoice_id.company_id.currency_id, line.as_invoice_id.company_id, line.as_invoice_id.invoice_date,round=True)
                        if self.as_payment_type == 'inbound':
                            credit_line = dict(base_line, account_id=credit_account_id,debit=0.00,credit=amount_pagar,invoice_id=line.as_invoice_id.id,analytic_account_id = line.as_analytic_account_id.id)
                        else:
                            credit_line = dict(base_line, account_id=credit_account_id,credit=0.00,debit=amount_pagar,invoice_id=line.as_invoice_id.id,analytic_account_id = line.as_analytic_account_id.id)
                        AccountMoveLine.append([0, 0, credit_line])
                        total_credit += amount_pagar
            if self.as_payment_type == 'inbound':
                debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
            else:
                debit_line = dict(base_line, account_id=debit_account_id,credit=total_credit,debit=0.00)
            AccountMoveLine.append([0, 0, debit_line])
        else:
            for line in self.as_sale_ids:
                monto = 0.0
                mont2 = 0.0
                if line.state == 'draft':
                    if line.as_amount > 0.0:
                        currency_id = self.currency_id
                        line.state = 'posted'
                        if (line.as_amount+amount_access) < line.as_amount_total:
                            monto = round(line.as_amount,2)
                            monto2 = round(line.as_amount_total,2)
                            parcial = True
                        else:
                            monto = round(line.as_amount_total,2)
                            monto2 = round(line.as_amount,2)
                        amount += currency_id._convert((monto2),line.as_invoice_id.company_id.currency_id, line.as_invoice_id.company_id, line.as_invoice_id.invoice_date,round=True)
                        amount_pagar = currency_id._convert((monto),line.as_invoice_id.company_id.currency_id, line.as_invoice_id.company_id, line.as_invoice_id.invoice_date,round=True)
                        if self.as_payment_type == 'inbound':
                            credit_line = dict(base_line, account_id=credit_account_id,debit=0.00,credit=amount_pagar,invoice_id=line.as_invoice_id.id,analytic_account_id = line.as_analytic_account_id.id)
                        else:
                            credit_line = dict(base_line, account_id=credit_account_id,credit=0.00,debit=amount_pagar,invoice_id=line.as_invoice_id.id,analytic_account_id = line.as_analytic_account_id.id)
                        AccountMoveLine.append([0, 0, credit_line])
                        total_credit += amount_pagar
            currency_difs = total_credit-amount
            currency_dif = abs( total_credit-amount)
            if currency_dif <= amount_access and currency_dif >= (amount_access*-1):
                if currency_dif >= 0.01 or currency_dif <= -0.01:
                    credit_line = self._create_accounting_dif(credit_diferencia,currency_dif,currency_difs,base_line,False,line.as_invoice_id.id)
                    AccountMoveLine.append([0, 0, credit_line])
                    total_credit += (currency_difs*-1)
            elif currency_difs < amount_access and parcial != True:
                if self.as_payment_type == 'inbound':
                    credit_line = dict(base_line, account_id=credit_anticipo,debit=0.00,credit=currency_dif,invoice_id=line.as_invoice_id.id)
                else:
                    credit_line = dict(base_line, account_id=credit_anticipo,credit=0.00,debit=currency_dif,invoice_id=line.as_invoice_id.id)
                AccountMoveLine.append([0, 0, credit_line])                    
                total_credit += currency_dif

            if self.as_payment_type == 'inbound':
                debit_line = dict(base_line, account_id=debit_account_id,debit=total_credit,credit=0.00)
            else:
                debit_line = dict(base_line2, account_id=debit_account_id,credit=total_credit,debit=0.00)
            AccountMoveLine.append([0, 0, debit_line])
            if self.journal_id.currency_id.id == 2:
                base_line2 = {
                'name': 'ITF'+' '+str(self.as_nota),
                'partner_id': self.as_partner_id.id,
                }
                base_line3 = {
                'name': 'ITF'+' '+str(self.as_nota),
                'partner_id': self.as_tesoreria_id.as_user_id.partner_id.id,
                }
                total_credit2 = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_itf_catidad'))
                debit_line2 = dict(base_line2, account_id=self.journal_id.as_itf.id,debit=total_credit2*total_credit,credit=0.00)
                AccountMoveLine.append([0, 0, debit_line2])
                credit_line2 = dict(base_line3, account_id=self.journal_id.payment_debit_account_id.id,debit=0.00,credit=total_credit2*total_credit)
                AccountMoveLine.append([0, 0, credit_line2])

        return AccountMoveLine


    def get_sale_process(self):
        amount_access = float(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_amount_access'))
        move_create = self.env['account.move']
        if not self.as_partner_id:
            raise UserError(_("Debe seleccionar un Cliente o Empresa!"))
        if not self.journal_id:
            raise UserError(_("Debe seleccionar un diario!"))
        if not self.currency_id:
            raise UserError(_("Debe seleccionar una moneda!"))
        if self.as_amount <= 0:
            raise UserError(_("El monto a pagar no puede ser cero!"))
        cant = len(self.as_sale_ids)
        cont = 0
        for line in self.as_sale_ids:
            if line.as_amount <= 0:
                cont+=1
        if cant == cont and self.as_type  not in ('anticipo','quincena','prestamos','Desembolso','Diferencia','quiquenio','individual','dividendo','multi_pago','asiento_asjuste','finiquito','Otros'):
            raise UserError(_("Monto a pagar en lineas no puede ser cero!"))
        account_in = self.journal_id.payment_debit_account_id.id
        if self.as_payment_type == 'inbound':
            account_out = self.as_partner_id.property_account_receivable_id.id
        else:
            account_out = self.as_partner_id.property_account_payable_id.id

        if self.as_payment_type == 'inbound' and self.as_type  not in ('anticipo','quincena','prestamos','Desembolso','Diferencia','quiquenio','individual','dividendo','multi_pago','asiento_asjuste','finiquito','Otros'):
            if self.as_is_anticipo:
                account_in = self.as_partner_id.property_account_anticipo_id.id
                account_out = self.as_partner_id.property_account_receivable_id.id
            line_move = self._create_accounting_entries_sale(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id
                for line in self.as_sale_ids:
                    if line.as_amount > 0.0:
                        line.write({'account_move_id': move.id})
                        if self.as_type == 'invoice':
                            for line_move in self.account_move_id.line_ids:
                                if line_move.account_id == self.as_partner_id.property_account_receivable_id and line.as_invoice_id == line_move.invoice_id:
                                    credit_aml = line_move
                                    line_move.reconciled = False
                                    line.as_invoice_id.js_assign_outstanding_line(credit_aml.id)
                                    sale = self.env['sale.order'].search([('name','=', line.as_invoice_id.invoice_origin)],limit=1)
                                    if sale:
                                        sale.ajustar_saldos(False)
                        line.as_sale_id.ajustar_saldos(False)
        elif self.as_payment_type == 'outbound' and self.as_type  not in ('anticipo','quincena','prestamos','Desembolso','Diferencia','quiquenio','individual','dividendo','multi_pago','asiento_asjuste','finiquito','Otros') :
            if self.as_is_anticipo:
                account_in = self.as_partner_id.property_account_supplier_id.id
                account_out = self.as_partner_id.property_account_payable_id.id
            line_move = self._create_accounting_entries_sale(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id
                for line in self.as_sale_ids:
                    if line.as_amount > 0.0:
                        line.write({'account_move_id': move.id})
                        if self.as_type == 'invoice':
                            for line_move in self.account_move_id.line_ids:
                                if line_move.account_id == self.as_partner_id.property_account_payable_id and line.as_invoice_id == line_move.invoice_id:
                                    credit_aml = line_move
                                    line_move.reconciled = False
                                    line.as_invoice_id.js_assign_outstanding_line(credit_aml.id)
                    line.as_invoice_id.ajustar_saldos(False)

        if self.as_type == 'anticipo':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.property_account_supplier_id.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.property_account_anticipo_id.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id
        if self.as_type == 'prestamos':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.as_cuenta_prestamos.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.as_cuenta_prestamos.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id

        if self.as_type == 'quiquenio':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.as_cuenta_quinquenio.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.as_cuenta_quinquenio.id
            line_move = self._create_accounting_entries_quinquenio(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id

        if self.as_type == 'dividendo':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.as_cuenta_dividendo.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.as_cuenta_dividendo.id
            line_move = self._create_accounting_entries_quinquenio(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id

        if self.as_type == 'Desembolso':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.as_account_viatic.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.as_account_viatic.id
            # line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            line_move = self._create_accounting_entries_rembolse(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id

        if self.as_type == 'Diferencia':
            if self.as_payment_type == 'outbound':
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.as_account_diff_viatic.id
            else:
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.as_account_diff_viatic.id
            line_move = self._create_accounting_entries_diferencia(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id

        if self.as_type == 'quincena':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.as_partner_id.as_cuenta_quincenas.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.as_partner_id.as_cuenta_quincenas.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id
        if self.as_type == 'multi_pago':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.journal_id.payment_credit_account_id.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.journal_id.payment_credit_account_id.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id
        if self.as_type == 'individual':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.journal_id.payment_credit_account_id.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.journal_id.payment_credit_account_id.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id
        if self.as_type == 'asiento_asjuste':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.journal_id.payment_credit_account_id.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.journal_id.payment_credit_account_id.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id   
        if self.as_type == 'finiquito':
            if self.as_payment_type == 'outbound':
                account_in = self.journal_id.payment_debit_account_id.id
                account_out = self.journal_id.payment_credit_account_id.id
            else:
                account_out = self.journal_id.payment_debit_account_id.id
                account_in = self.journal_id.payment_credit_account_id.id
            line_move = self._create_accounting_entries_anticipo(account_in,account_out)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id        
        if self.as_type == 'Otros':
            account_in = self.as_account_debit.id
            account_out = self.as_account_credit.id
            line_move = self._create_accounting_entries_anticipo(account_out,account_in)
            if line_move != []:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'date': (datetime.strptime(str(self.date),'%Y-%m-%d %H:%M:%S') - relativedelta(hours=4)),
                    'ref': self.as_nota,
                    'line_ids': [],
                }
                move_vals['line_ids']+= line_move 
                move = move_create.create(move_vals)
                move.post()
                self.account_move_id = move.id

        self.state = 'confirm'


class AsPaymentMultiLine(models.Model):
    _name = 'as.payment.multi.line'

    name = fields.Char('Ref. Interna')
    as_sale_id = fields.Many2one('sale.order', string="Venta")
    as_invoice_id = fields.Many2one('account.move', string="Factura")
    as_amount_total = fields.Float('Saldo')
    as_amount = fields.Float('Monto a Pagar')
    payment_id = fields.Many2one('account.payment', string="Pago Generado")
    account_move_id = fields.Many2one('account.move', string="Pago Generado")
    account_movea_id = fields.Many2one('account.move', string="Anticipo Generado")
    paymenta_id = fields.Many2one('account.payment', string="Anticipo Generado")
    state = fields.Selection([('draft', 'Borrador'), ('posted', 'Posteado'), ('sent', 'Enviado'), ('reconciled', 'Reconciliado'), ('cancelled', 'Cancelado')], readonly=True, default='draft', copy=False, string="Estado")
    date = fields.Date(string='Fecha de Venta', default=fields.Date.context_today)
    currency_id = fields.Many2one('res.currency', 'Moneda')
    as_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica')

    def get_cancel_payment(self):
        for payment in self:
            payment.state = 'cancelled'
            payment.payment_id.cancel()


class SaleAdvancePaymentLine(models.Model):
    _name = "as.sale.payment.line"

    payment_id = fields.Many2one('account.payment', 'Anticipo')
    currency_id = fields.Many2one('res.currency', 'Moneda')
    amount_to_pay = fields.Monetary(string='Monto')
    is_pago = fields.Boolean(string="Usar")
    move_line_id  = fields.Many2many('account.move', string='Linea asiento')
