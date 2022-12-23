# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Accountaccount(models.Model):
    _inherit = "account.account"

    as_is_terceros = fields.Boolean(string='Es cuenta de Pago a Terceros')


class AccountMove(models.Model):
    _inherit = "account.move"

    as_payslip_run = fields.Many2one('hr.payslip.run', string='Nomina')
