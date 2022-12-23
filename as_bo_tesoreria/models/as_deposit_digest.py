# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)
class Aschecks(models.Model):
    "Modulo de Control de depositos de cheques y efectivo en Tesoreria"
    _name = 'as.deposit.digest'
    _description = 'Modulo de Control de depositos de cheques y efectivo en Tesoreria'

    name = fields.Char('Titulo')
    as_date = fields.Date("Fecha", default=fields.Date.today)
    state = fields.Selection(selection=[('draft', 'Borrador'), ('confirm', 'Confirmado'), ('cancel', 'Cancelado')], string="Estado", default='draft')
    as_folio = fields.Char('Folio',required=True)
    as_company_id = fields.Many2one('res.company', string="Compañia",default=lambda self: self.env.company.id)
    as_partner_id = fields.Many2one('res.partner', string="Cliente",related="as_company_id.partner_id")
    as_account_bank_id = fields.Many2one('res.partner.bank', string="Banco Destino",domain="[('partner_id','=',as_partner_id )]")
    as_num_cuenta = fields.Char('Nro de Cuenta')
    as_type_deposit = fields.Selection([('Efectivo', 'Efectivo'), ('check_date', 'CHEQUE A LA FECHA'),('check_day', 'CHEQUE AL DIA')], string="Tipo", default='Efectivo')
    as_tesoreria_id = fields.Many2one('as.tesoreria',string="Caja de Tesoreria",required=True)
    as_checks_ids = fields.Many2many('as.check.control',string="Cheques",)
    as_amount = fields.Float('Monto')
    as_amount_check = fields.Float('Monto Documento',readonly=True)
    as_amount_diff = fields.Float('Diferencia')
    as_currency_id = fields.Many2one('res.currency', string="Moneda",required=True,default=lambda self: self.env.company.currency_id.id)
    as_extract_efectivo = fields.Boolean(string='Extraer total de ingreso')

    @api.onchange('as_account_bank_id')
    def as_get_account(self):
        self.as_num_cuenta = self.as_account_bank_id.acc_number

    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('account.deposit')
            vals_product['name'] = secuence
        templates = super().create(vals_list)
        if templates.as_amount <= 0.0:
            raise UserError('El monto no puede ser Cero!!.')
        for check in templates.as_checks_ids:
            check.state = 'in_wallet'
        return templates


    def cancel_payment_deposit(self):
        self.state = 'cancel'
        for check in self.as_checks_ids:
            check.state = 'draft'


    @api.onchange('as_checks_ids','as_amount')
    def get_amount_checks(self):
        amount = 0.0
        for check in self.as_checks_ids:
            amount += check.as_amount
        if self.as_type_deposit == 'Efectivo':
            self.as_get_extract()
            self.as_amount_diff = self.as_amount - self.as_amount_check
        else:
            self.as_amount_diff = self.as_amount - self.as_amount_check
            self.as_amount_check = amount
    
    @api.onchange('as_extract_efectivo')
    def as_get_extract(self):
        total_ingreso = 0.0
        if self.as_tesoreria_id:
            total_ingreso = self.as_tesoreria_id.as_amount_total_ingreso
        if self.as_extract_efectivo:
            self.as_amount_check = total_ingreso
        else:
            self.as_amount_check = 0.0
        self.as_amount_diff = self.as_amount - self.as_amount_check


             
