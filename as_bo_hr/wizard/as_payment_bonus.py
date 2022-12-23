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
    _name="as.payment.finiquito"
    _description="empleados a seleccionar"

    as_generador_id = fields.Many2one('as.hr.finiquito', string='Procesamiento de Nomina')
    as_journal_id = fields.Many2one('account.journal', string="Diario",required=True)
    as_date = fields.Date("Fecha", default=fields.Date.today,required=True)
    as_glosa = fields.Char(string="Glosa")
    as_type =  fields.Selection([('finiquito', 'Liquidación o Indemnización')],default="finiquito", string="Tipo Documento", required=True)
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
        total = self.as_generador_id.as_total
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
            'as_type': self.as_type,
        }
        payment = self.env['as.payment.multi'].create(registro)
        movimeintos = []
        for mov in self.as_generador_id.as_caja_line_id:
            movimeintos.append(mov.id)
        movimeintos.append(payment.id)
        self.as_generador_id.as_caja_line_id = movimeintos
        self.as_generador_id.state = 'paid'


