# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import re
import xlrd
from xlrd import open_workbook
from datetime import datetime, timedelta
import base64
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError

_logger = logging.getLogger(__name__)


class as_hr_employees(models.Model):
    _name = "as.payment.terceros"
    _description = "seleccionar pagos a terceros para tesoreria"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina", required=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    as_journal_id = fields.Many2one('account.journal', 'Diario')
    journal_entry_id = fields.Many2one('account.journal', 'Diario Asiento Ajuste', domain=[('type', '=', 'general')])
    account_id = fields.Many2one('account.account', string='Cuenta de Ajuste',
                                 domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", required=True)

    @api.model
    def default_get(self, fields):
        res = super(as_hr_employees, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        dictline = []
        dictlinestock = []
        stock = 1
        menor = 0.0
        value = 0.0
        moveids = []
        if res_ids and res_ids[0]:
            so_line = res_ids[0]
            hr_run = self.env['hr.payslip.run'].browse(so_line)
            for mov in hr_run.slip_ids:
                if mov.move_id:
                    if mov.move_id.id not in moveids:
                        moveids.append(mov.move_id.id)
            move_ids = self.env['account.move'].search([('id', 'in', moveids)])
            for mv in move_ids:
                for linea in mv.line_ids:
                    if linea.account_id.as_is_terceros:
                        dictlinestock.append(linea.id)

            res.update({
                'payslip_run_id': hr_run.id,
            })
        return res

    def action_generate(self):
        moveids = []
        for row in self:
            for mov in row.payslip_run_id.slip_ids:
                if mov.move_id:
                    if mov.move_id.id not in moveids:
                        moveids.append(mov.move_id.id)
            move_ids = self.env['account.move'].search([('id', 'in', moveids)])

            total = 0
            total_credit = 0
            account_pay = []
            # Agrupar por cuenta contable
            for line in move_ids[0].line_ids:
                if line.credit > 0 and line.account_id.as_is_terceros:
                    if not line.partner_id:
                        raise UserError(_(
                            "Debe definir un contacto para la cuenta: %s, cambie a borrador el asiento de la planilla actual y edite la información")
                                        % (line.account_id.display_name))
                    else:
                        account_pay.append(line.account_id.id)
            acc_pp = list(dict.fromkeys(account_pay))

            if move_ids[0].state != 'posted':
                raise UserError(_(
                    "Debe confirmar el asiento contable de la planilla actual"))
            # Asiento 1

            AccountMove = self.env['account.move']

            for acc_p in acc_pp:
                move_line_recon = self.env['account.move.line']
                lines_ids_a = []
                tot_cuenta = 0
                partner_id = False
                date = False
                ref = ''
                for line in move_ids[0].line_ids.filtered(lambda m: m.account_id.id == acc_p and m.credit > 0):
                    tot_cuenta += line.credit
                    partner_id = line.partner_id
                    date = line.date
                    ref = line.account_id.display_name
                    move_line_recon |= line

                debit_val = {
                    'name': 'Asiento Ajuste',
                    'account_id': self.account_id.id,
                    'credit': tot_cuenta,
                    'debit': 0,
                }
                lines_ids_a.append(debit_val)
                credit_val = {
                    'name': 'Asiento Ajuste',
                    'account_id': acc_p,
                    'credit': 0,
                    'partner_id': partner_id.id,
                    'debit': tot_cuenta
                }
                lines_ids_a.append(credit_val)

                move = AccountMove.create({
                    'partner_id': partner_id.id,
                    'journal_id': self.journal_entry_id.id,
                    'line_ids': [(0, 0, line_vals) for line_vals in lines_ids_a],
                    'date': date,
                    'ref': 'Asiento reversion por cobrar ' + ref,
                    'move_type': 'entry',
                })
                move.post()
                line_to_reconcile = move.line_ids.filtered(lambda line2: line2.debit > 0 and
                                                                         line2.credit == 0 and
                                                                         not line2.reconciled and
                                                                         line2.account_id.internal_type == 'payable' and
                                                                         line2.account_id.id == acc_p)
                move_line_recon |= line_to_reconcile
                move_line_recon.reconcile()
                account_rev = self.env['account.account'].browse(acc_p)
                if partner_id.property_account_payable_id.id != acc_p:
                    raise UserError(_(
                        "El contacto: %s, tiene asignada la cuenta por pagar %s, debe asignarle la cuenta %s")
                                    % (partner_id.name, partner_id.property_account_payable_id.display_name,
                                       account_rev.display_name))
                accoun_obj = self.env['account.move']
                partner_search = self.env.user.company_id.partner_id
                pur_date = datetime.today()
                vals = {
                    'journal_id': self.as_journal_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'invoice_date': pur_date,
                    'move_type': 'in_invoice',
                    'partner_id': partner_id.id,
                    'as_contable': True,
                    'as_payslip_run': self.payslip_run_id.id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': '',
                            'quantity': 1,
                            'account_id': self.account_id.id,
                            'price_unit': tot_cuenta,
                            'tax_ids': [],
                        }),
                    ]
                }
                pur_id = accoun_obj.create(vals)
                # pur_id.action_post()

            line_ids = []
            date = False
            for line in move_ids[0].line_ids:
                if line.debit > 0:
                    date = line.date
                    debit_val = {
                        'name': line.name + 'Volteo por Factura Proveedor',
                        'account_id': line.account_id.id,
                        'credit': line.debit,
                        'debit': 0,
                    }
                    total += line.debit
                    line_ids.append(debit_val)
            credit_val = {
                'name': 'Volteo asiento RRHH',
                'account_id': self.account_id.id,
                'credit': 0,
                'debit': total
            }
            line_ids.append(credit_val)
            move = AccountMove.create({
                'journal_id': self.journal_entry_id.id,
                'line_ids': [(0, 0, line_vals) for line_vals in line_ids],
                'date': date,
                'ref': 'Volteo cuenta de gasto asiento RRHH',
                'move_type': 'entry',
            })
            move.post()
        # for mv in move_ids:
        #     for linea in mv.line_ids:
        #         if linea.account_id.as_is_terceros:
        #             row.as_create_account_move(linea.account_id.id, linea.credit, linea.name + '-' + str(cont))
        #             cont += 1


def as_create_account_move(self, account_id, amount, name):
    amount = round(amount, 2)
    accoun_obj = self.env['account.move']
    partner_search = self.env.user.company_id.partner_id
    pur_date = datetime.today()
    vals = {
        'journal_id': self.as_journal_id.id,
        'currency_id': self.env.user.company_id.currency_id.id,
        # 'date': pur_date,
        'invoice_date': pur_date,
        'move_type': 'in_invoice',
        'partner_id': partner_search.id,
        # 'ref': name,
        'as_contable': True,
        'as_payslip_run': self.payslip_run_id.id,
        'invoice_line_ids': [
            (0, 0, {
                'name': name,
                'quantity': 1,
                'account_id': self.account_id.id,
                'price_unit': amount,
                'tax_ids': [],
            }),
        ]
    }
    pur_id = accoun_obj.create(vals)
    # pur_id.action_post()
