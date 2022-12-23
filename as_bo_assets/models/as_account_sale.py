# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AsAccountSale(models.Model):
    _name = 'as.account.sale'
    _description = 'Para almacenar cuentas para asientos de venta'

    name = fields.Char(string="Titulo")
    #asiento venta 1
    as_account_1_debit_id = fields.Many2one('account.account', string='Cuenta Asiento 1 (Debe)', domain=[('deprecated', '=', False)])
    as_account_1_credit_id = fields.Many2one('account.account', string='Cuenta Asiento 1 (Haber)', domain=[('deprecated', '=', False)])
    #asiento venta 2
    as_account_2_debit_id = fields.Many2one('account.account', string='Cuenta Asiento 2 (Debe)', domain=[('deprecated', '=', False)])
    as_account_2_credit_id = fields.Many2one('account.account', string='Cuenta Asiento 2 (Haber)', domain=[('deprecated', '=', False)])
    #asiento venta 3
    as_account_2_debit_id = fields.Many2one('account.account', string='Cuenta Asiento 2 (Debe)', domain=[('deprecated', '=', False)])
    as_account_2_credit_id = fields.Many2one('account.account', string='Cuenta Asiento 2 (Haber)', domain=[('deprecated', '=', False)])
    #siento venta 4
    as_account_3_caj_id = fields.Many2one('account.account', string='Cuenta caja o banco', domain=[('deprecated', '=', False)])
    as_account_3_itc_id = fields.Many2one('account.account', string='Cuenta Asiento 3 IT por cobrar', domain=[('deprecated', '=', False)])
    as_account_3_itp_id = fields.Many2one('account.account', string='Cuenta Asiento 3 IT por pagar', domain=[('deprecated', '=', False)])
    as_account_3_dep_id = fields.Many2one('account.account', string='Cuenta Asiento 3 depreciación Acum.', domain=[('deprecated', '=', False)])
    as_account_3_her_id = fields.Many2one('account.account', string='Cuenta Asiento 3 Herramientas', domain=[('deprecated', '=', False)])
    as_account_3_iva_id = fields.Many2one('account.account', string='Cuenta Asiento 3 IVA DEF', domain=[('deprecated', '=', False)])
    as_account_3_oin_id = fields.Many2one('account.account', string='Cuenta Asiento 3 Otros Ingresos', domain=[('deprecated', '=', False)])
    #cuentas para dar de baja
    as_discharged_debit_id = fields.Many2one('account.account', string='Cuenta Dar de baja (Debe)', domain=[('deprecated', '=', False)])
    as_discharged_credit_id = fields.Many2one('account.account', string='Cuenta Dar de baja (Haber)', domain=[('deprecated', '=', False)])