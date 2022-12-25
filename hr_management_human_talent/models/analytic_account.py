from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    direct_indirect = fields.Selection(selection=[('direct', 'Direct'), ('indirect', 'Indirect')])
