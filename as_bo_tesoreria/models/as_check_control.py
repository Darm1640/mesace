# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
class Aschecks(models.Model):
    "Modulo de Control de Cheques en Tesoreria"
    _name = 'as.check.control'
    _description = 'Modulo de Control de Cheques en Tesoreria'


    name = fields.Char('Titulo',readonly=True)
    as_company_id = fields.Many2one('res.company', string="Compañia",required=True,default=lambda self: self.env.company.id)
    as_type_ckeck = fields.Selection([('check_day', 'CHEQUE AL DIA'), ('check_date', 'CHEQUE A LA FECHA')], string="Tipo de Cheque", default='check_day')
    as_num_ckeck = fields.Char('Nro de Cheque')
    as_account_origin = fields.Char('Cuenta Nro Origen',required=True)
    as_account_bank_id = fields.Many2one('res.partner.bank', string="Banco",domain="[('partner_id','=', as_partner_id)]")
    as_date_expire = fields.Date("Fecha de Vencimiento", default=fields.Date.today)
    as_date = fields.Date("Fecha", default=fields.Date.today)
    as_vat = fields.Char('RUT',required=True)
    state = fields.Selection(selection=[('draft', 'En Cartera'),('in_wallet', 'En Deposito'), ('collected', 'Cobrado'), ('protested', 'Protestado'),('extended', 'Prorrogado'), ('cancel', 'Cancelado')], string="Estado", default='draft')
    as_currency_id = fields.Many2one('res.currency', string="Moneda",required=True,default=lambda self: self.env.company.currency_id.id)
    as_user_id = fields.Many2one('res.users', string="Usuario",required=True,default=lambda self: self.env.user.id)
    as_amount = fields.Float('Monto')
    as_partner_id = fields.Many2one('res.partner', string="Cliente")
    as_reason = fields.Many2one('as.reason.checks', string="Motivo")

    @api.onchange('as_account_bank_id')
    def as_get_account(self):
        self.as_account_origin = self.as_account_bank_id.acc_number

    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            if vals_product['as_type_ckeck'] =='check_day':
                secuence =  self.env['ir.sequence'].next_by_code('account.checks.day')
                vals_product['name'] = secuence
            else:
                secuence =  self.env['ir.sequence'].next_by_code('account.checks.date')
                vals_product['name'] = secuence  
        templates = super().create(vals_list)
        if templates.as_amount <= 0.0:
            raise UserError('El monto no puede ser Cero!!.')
        return templates

    @api.onchange('as_date_expire','as_date_expire','as_date')
    def get_amount_date(self):
        for check in self:
            if check.as_type_ckeck == 'check_day':
                check.as_date_expire = check.as_date


    @api.onchange('as_partner_id')
    def get_amount_partner_id(self):
        for check in self:
            self.as_vat = self.as_partner_id.vat



    
class Aschecks(models.Model):
    "Modulo de registros de motivos de anulacion o prorroga"
    _name = 'as.reason.checks'
    _description = 'Modulo de registros de motivos de anulacion o prorroga'

    name = fields.Char(string="Motivo")
