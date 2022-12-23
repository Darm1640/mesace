# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsPaymentCreate(models.Model):
    _name = 'as.liquidation.tbank'
    _description="Liquidador de cuotas transbank"
    _order = 'date'

    name = fields.Float(string="Tituto",readonly=True)
    date_start = fields.Date("Fecha Inicial", default=fields.Date.today)
    date_end = fields.Date("Fecha Fin", default=fields.Date.today)
    account_id = fields.Many2one('account.account', string="Cuenta")
    account_bank_id = fields.Many2one('account.account', string="Cuenta Banco")
    account_move_ids = fields.Many2many('account.move.line', string="Cuotas")
    as_move_id = fields.Many2one('account.move', string="Asiento de liquidación")

    @api.onchange('date_start','date_end','account_id')
    def as_get_cuotas_payment(self):
        moves_account = []
        if self.account_id:
            moves = self.env['account.move'].search([('date','>=',str(self.date_start)),('date','<=',str(self.date_end))])
            consulta = """select aml.id from account_move_line aml
                    join account_move am on am.id=aml.move_id
                    where am.state = 'posted' and (aml.as_liquidado_move = false or aml.as_liquidado_move is null) and aml.date_maturity >= '"""+str(self.date_start)+"""' and aml.invoice_id is not null and aml.date_maturity <='"""+str(self.date_end)+"""' and aml.account_id ="""+str(self.account_id.id)
            self.env.cr.execute(consulta) 
            for move_line_id in self.env.cr.fetchall():
                moves_account.append(move_line_id[0])
            if moves_account != []:
                self.account_move_ids = moves_account    
            else:
                self.account_move_ids = []


    @api.model
    def create(self, vals):
        result = super(AsPaymentCreate, self).create(vals)
        AccountMoveLine = []
        move_create = self.env['account.move']
        journal_id= self.env['account.journal'].search([('default_account_id','=',result.account_id.id)],limit=1)
        move_vals = {
            'journal_id': journal_id.id,
            'date': result.date_start,
            'ref': 'Liquidación de Cuotas Transbank del '+str(result.date_start.strftime('%d-%m-%Y'))+' al '+str(result.date_end.strftime('%d-%m-%Y')),
            'line_ids': [],
        }
        total_debe = 0.0
        for line in result.account_move_ids:
            base_line = {
                'name': line.name,
                'partner_id': line.partner_id.id,
                'date':  result.date_start,
                # 'analytic_account_id': result.as_partner_id.account_analytic_id.id,
            }
            total_debe += line.debit
            credit_line = dict(base_line, account_id=result.account_id.id,debit=0.0,date_maturity=line.date_maturity,credit=line.debit,invoice_id=line.invoice_id.id)
            AccountMoveLine.append([0, 0, credit_line])
        debit_line = dict(base_line, account_id=result.account_bank_id.id,debit=total_debe,date_maturity=line.date_maturity,credit=0.0,invoice_id=line.invoice_id.id)
        AccountMoveLine.append([0, 0, debit_line])

        move_vals['line_ids']+= AccountMoveLine 
        move = move_create.create(move_vals)
        result.as_move_id = move
        for line in result.as_move_id.line_ids:
            line.as_liquidado_move = True
        
        return result