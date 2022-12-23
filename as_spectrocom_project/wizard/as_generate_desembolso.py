# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError
import re
import xlrd
from xlrd import open_workbook
import math
from odoo import tools
import logging
from io import BytesIO
from datetime import datetime, timedelta
from odoo.tests import Form
import base64
_logger = logging.getLogger(__name__)

class as_generare_reembolso(models.Model):
    _name="as.generate.tesoreria"
    _description="Modelo para generar registro de ingreso o egreso a partir de tesoreria"

    as_type = fields.Selection([('anticipo', 'Anticipo'),('Desembolso', 'Desembolso'),('Diferencia', 'Diferencia')], string="Tipo Documento", default='Desembolso', required=True)
    as_journal_id = fields.Many2one('account.journal', "Diario")
    as_payment_acquirer_id = fields.Many2one('as.payment.acquirer', string='Método de Pago',required=True)
    as_numero_documento = fields.Char('Nro documento', help=u'Número del documento del banco.')
    as_recibo_manual = fields.Char('Nro documento', help=u'Número del documento del banco.')
    as_metodo_pago_bolean = fields.Integer(related='as_payment_acquirer_id.tipo_documento', string="Boolean")
    as_payment_type = fields.Selection([('inbound', 'Ingreso'), ('outbound', 'Egreso')], string="Tipo de Pago",required=True,default="inbound")
    as_amount = fields.Float(string="Monto a Pagar",  required=True)
    as_partner_id = fields.Many2one('res.partner', string="Cliente/Empresa")
    as_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica')
    as_note = fields.Char(string="Detalle")
    as_bank_id = fields.Many2one('res.partner.bank', string="Banco",domain="[('partner_id','=', as_partner_id)]")
    as_task_id = fields.Many2one('project.task', 'Tarea')
    as_caja_id = fields.Many2one('as.tesoreria', 'Caja',required=True)
    as_is_diff = fields.Boolean('Es Diferencia')
    as_is_diff_negativa = fields.Boolean('Es Diferencia negativa')
    date = fields.Datetime(string='Fecha de pago', default=fields.Datetime.now())

    @api.model
    def default_get(self, fields):
        res = super(as_generare_reembolso, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        as_modelo = self._context.get('active_model')
        so_line_obj = self.env[as_modelo].browse(res_ids)
        res['as_task_id'] = so_line_obj.id
        res['as_partner_id'] = so_line_obj.user_id.partner_id.id
        res['as_analytic_account_id'] = so_line_obj.as_analytic_account_id.id
        total_pagar = 0.0
        if not self._context.get('default_as_is_diff'):
            total_pagar=so_line_obj.as_saldo_reembolso
            res['as_payment_type'] = 'outbound'
            res['as_type'] = 'Desembolso'
            if total_pagar == 0.0 and so_line_obj.as_saldo_diferencia_negativa < 0:
                total_pagar= abs(so_line_obj.as_saldo_diferencia_negativa)
                res['as_is_diff_negativa'] = True
        else:
            res['as_payment_type'] = 'inbound'
            res['as_type'] = 'Diferencia'
            total_pagar=so_line_obj.as_saldo_diferencia

        res['as_amount'] = total_pagar
        if total_pagar <= 0.0:
            raise UserError(_("No puede generar desembolso o diferencia con saldo cero"))
        caja = self.env['as.tesoreria'].search([('as_user_id','=',self.env.user.id),('state','=','open')])
        if not caja:
            raise UserError(_("No tiene una caja abierta para generar desembolso"))
        return res

    @api.onchange('as_partner_id','as_analytic_account_id','as_journal_id')
    def as_note_detalle(self):
        self.as_note = str(self.as_journal_id.name or '')+' - '+str(self.as_partner_id.name or '')+' - '+str(self.as_analytic_account_id.name or '')

    def as_get_process(self):
        if not self.as_journal_id: 
            raise UserError(_("El diario se requiere"))
        if not self.as_partner_id: 
            raise UserError(_("El Cliente/empresa se  requiere"))
        if self.as_amount == 0.0: 
            raise UserError(_("Monto no puede ser cero"))
        caja = self.as_caja_id
        if not caja:
            raise UserError(_("No hay Caja en estado Abierta"))
        registro = {
            'as_payment_type':self.as_payment_type,
            'as_partner_id':self.as_partner_id.id,
            'journal_id':self.as_journal_id.id,
            'payment_acquirer_id':self.as_payment_acquirer_id.id,
            'as_numero_documento':self.as_numero_documento,
            'as_bank_id':self.as_bank_id.id,
            'as_amount': abs(self.as_amount),
            'date':self.date,
            'currency_id':self.as_journal_id.currency_id.id,
            'as_nota':self.as_note,
            'state': 'new',
            'as_tesoreria_id': caja.id,
            'as_project_id': self.as_task_id.id,
            'as_analytic_account_id': self.as_analytic_account_id.id,
            'as_type': self.as_type,
        }
        if self.as_is_diff:
            if self.as_amount < 0:
                registro['as_payment_type'] = 'outbound'
            else:
                registro['as_payment_type'] = 'inbound'
        if self.as_is_diff_negativa:
            registro['as_is_negativo'] = True
        payment = self.env['as.payment.multi'].create(registro)
        self.as_task_id._compute_saldo_reembolso()
        self.as_task_id._compute_saldo_diferencia()
        self.as_task_id._compute_saldo_diferencia_negativa()
