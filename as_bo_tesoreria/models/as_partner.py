# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "res.partner"

    def _compute_anticipo_count(self):
        result = self.env['account.move.line'].search([('partner_id','=',self.id),('account_id','=',self.property_account_anticipo_id.id),('move_id.state','=','posted')])
        result_supplier = self.env['account.move.line'].search([('partner_id','=',self.id),('account_id','=',self.property_account_supplier_id.id),('move_id.state','=','posted')])
        for order in self:
            order.as_anticipo_count = (sum(result.mapped('debit'))-sum(result.mapped('credit')))*-1
            order.as_anticipo_supplier_count = sum(result_supplier.mapped('debit'))-sum(result_supplier.mapped('credit'))

    property_account_supplier_id = fields.Many2one('account.account', company_dependent=True,string="Cuenta Proveedor Anticipo",domain=[('deprecated', '=', False)])
    property_account_anticipo_id = fields.Many2one('account.account', company_dependent=True,string="Cuenta Cliente Anticipo",domain=[('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica', groups="analytic.group_analytic_accounting")
    as_cuenta_prestamos = fields.Many2one('account.account','Cuentas prestamo empleado')
    as_cuenta_quincenas = fields.Many2one('account.account','Cuenta pago Aguinaldo')
    as_account_viatic = fields.Many2one('account.account','Cuenta Viaticos')
    as_account_diff_viatic = fields.Many2one('account.account','Cuenta Diferencia Viaticos')
    as_is_user = fields.Boolean(string='Es usuario',compute='_as_get_is_user')
    as_anticipo_count = fields.Float(compute='_compute_anticipo_count')
    as_anticipo_supplier_count = fields.Float(compute='_compute_anticipo_count')
    as_cuenta_quinquenio = fields.Many2one('account.account','Cuenta Anticipo Quinquenio')
    as_cuenta_dividendo = fields.Many2one('account.account','Cuenta Anticipo Dividendo')
    as_cuenta_employee = fields.Many2one('account.account','Cuenta Anticipo Empleado')
    as_interes = fields.Float(string='Intereses ', default=0.0)

    def _as_get_is_user(self):
        for partner in self:
            as_is_user = False
            user = self.env['res.users'].search([('partner_id','=',self.id)])
            if user:
                as_is_user = True
            partner.as_is_user = as_is_user

    def action_request_anticipo(self):
        self.ensure_one()
        action_hr_expense = self.env.ref('account.action_account_moves_all_tree')
        action = action_hr_expense.read()[0]
        action['context'] = {}
        result = self.env['account.move.line'].search([('partner_id','=',self.id),('account_id','=',self.property_account_anticipo_id.id),('move_id.state','=','posted')])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def action_request_antisupplier(self):
        self.ensure_one()
        action_hr_expense = self.env.ref('account.action_account_moves_all_tree')
        action = action_hr_expense.read()[0]
        action['context'] = {}
        result = self.env['account.move.line'].search([('partner_id','=',self.id),('account_id','=',self.property_account_supplier_id.id),('move_id.state','=','posted')])
        action['domain'] = [('id', 'in', result.ids)]
        return action