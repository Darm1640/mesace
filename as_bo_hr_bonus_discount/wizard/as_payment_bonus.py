# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import re
import xlrd
from xlrd import open_workbook
import base64
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
_logger = logging.getLogger(__name__)

class as_hr_employees(models.Model):
    _name="as.payment.bonus"
    _description="empleados a seleccionar"

    as_generador_id = fields.Many2one('as.generate.bonus.discount', string='Procesamiento de Nomina')
    as_journal_id = fields.Many2one('account.journal', string="Diario",required=True)
    as_date = fields.Date("Fecha", default=fields.Date.today,required=True)
    as_glosa = fields.Char(string="Glosa")
    as_type =  fields.Selection([('anticipo', 'Anticipo'),('prestamos', 'Prestamos'),('quincena', 'Aguinaldo'),('Desembolso', 'Desembolso'),('Diferencia', 'Diferencia'),('quiquenio', 'Anticipo Quinquenio'),('dividendo', 'Anticipo Dividendos'),('multi_pago', 'Multipago Quincena')],default="prestamos", string="Tipo Documento", required=True)
    as_payment_type = fields.Selection([('inbound', 'Ingreso'), ('outbound', 'Egreso')], string="Tipo de Pago",required=True,default="inbound")
    as_payment_acquirer_id = fields.Many2one('as.payment.acquirer', string='Método de Pago',required=True)
    as_numero_documento = fields.Char('Nro documento', help=u'Número del documento del banco.')
    as_recibo_manual = fields.Char('Nro documento', help=u'Número del documento del banco.')
    as_metodo_pago_bolean = fields.Integer(related='as_payment_acquirer_id.tipo_documento', string="Boolean")
    as_caja_id = fields.Many2one('as.tesoreria', 'Caja',required=True)
    as_bank_id = fields.Many2one('res.partner.bank', string="Banco")

    @api.onchange('as_journal_id','as_date','as_payment_acquirer_id')
    def as_onchange_caja(self):
        self.as_glosa = str(self.as_journal_id.name)+'-'+str(self.as_date)+'-'+str(self.as_payment_acquirer_id.name)

    def as_get_cargar_empleados(self):
        self.ensure_one()
        account_line_obj = self.env['account.move.line']
        if not self.as_journal_id: 
            raise UserError(_("El diario se requiere"))
        caja = self.as_caja_id
        if not caja:
            raise UserError(_("No hay Caja en estado Abierta"))
        if caja.state != 'open':
            raise UserError(_("La caja actual no esta abierta"))
        total = 0.0 
        for line in self.as_generador_id.as_summary_ids:
            if line.state == 'done' and line.as_pagar:
                total+=line.as_bonus_amount
        registro = {
            'as_payment_type':self.as_payment_type,
            'as_partner_id': self.env.user.company_id.partner_id.id,
            'journal_id':self.as_journal_id.id,
            'payment_acquirer_id':self.as_payment_acquirer_id.id,
            'as_numero_documento':self.as_numero_documento,
            'as_bank_id':self.as_bank_id.id,
            'as_amount': abs(total),
            'date':self.as_date,
            'currency_id':self.as_journal_id.currency_id.id,
            'as_nota':self.as_glosa,
            'state': 'new',
            'as_tesoreria_id': caja.id,
            # 'as_project_id': self.as_task_id.id,
            # 'as_analytic_account_id': self.as_analytic_account_id.id,
            'as_type': self.as_type,
        }
        payment = self.env['as.payment.multi'].create(registro)
        payment.account_move_id.button_draft()
        payment.account_move_id.line_ids.unlink()
        res = {
            'move_id': payment.account_move_id.id,
            'name': self.as_generador_id.name+' a '+self.env.user.company_id.partner_id.name,
            'partner_id': self.env.user.company_id.partner_id.id,
            # 'analytic_account_id': account_analityc.id,
            'account_id': self.as_journal_id.payment_debit_account_id.id,
            'date_maturity':self.as_date,
            'debit': 0.0,
            'credit': total,
            'amount_currency':total,
            }
        account_line_obj.with_context(check_move_validity=False).create(res)
        for line in self.as_generador_id.as_summary_ids:
            if line.state == 'done' and line.as_pagar:
                if not  line.as_employee_id.user_id:
                    raise UserError(_("%s no posee ficha de usuario") % line.as_employee_id.name)
                partner_id = line.as_employee_id.user_id.partner_id
                account_id = partner_id.as_cuenta_employee.id
                if self.as_type == 'anticipo':
                    account_id = partner_id.property_account_supplier_id.id
                elif self.as_type == 'prestamos':
                    account_id = partner_id.as_cuenta_prestamos.id
                elif self.as_type == 'quiquenio':
                    account_id = partner_id.as_cuenta_quinquenio.id
                elif self.as_type == 'dividendo':
                    account_id = partner_id.as_cuenta_dividendo.id    
                elif self.as_type == 'Desembolso':
                    account_id = partner_id.as_account_viatic.id    
                elif self.as_type == 'Diferencia':
                    account_id = partner_id.as_account_diff_viatic.id
                elif self.as_type == 'quincena':
                    account_id = partner_id.as_cuenta_quincenas.id
                elif self.as_type == 'multi_pago':
                    account_id = partner_id.as_cuenta_employee.id        
                res = {
                    'move_id': payment.account_move_id.id,
                    'name': self.as_generador_id.name+' a '+partner_id.name,
                    'partner_id': partner_id.id,
                    # 'analytic_account_id': account_analityc.id,
                    'account_id': account_id,
                    'date_maturity':self.as_date,
                    'debit': line.as_bonus_amount,
                    'credit': 0.0,
                    'amount_currency':line.as_bonus_amount,
                    }
                account_line_obj.with_context(check_move_validity=False).create(res)
                line.state = 'close'
                line.as_pagar = False
        payment.account_move_id.action_post()
        movimeintos = []
        for mov in self.as_generador_id.as_caja_line_id:
            movimeintos.append(mov.id)
        movimeintos.append(payment.id)
        self.as_generador_id.as_caja_line_id = movimeintos

        cantidad = len(self.as_generador_id.as_summary_ids)
        cantidad2 = len(self.as_generador_id.as_summary_ids.filtered(lambda r: r.state == 'close'))
        if cantidad == cantidad2:
            self.as_generador_id.state = 'close'



class as_hr_employees_line(models.Model):
    _name="as.hr.employees.line"
    _description="empleados a seleccionar"

    as_employee_id = fields.Many2one('hr.employee', string='Empleado')
    as_action = fields.Boolean(string='Seleccionar')
    as_generator_id = fields.Many2one('as.hr.employees', string='padre')