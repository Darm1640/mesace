from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    as_sequence_wa_id = fields.Many2one('ir.sequence', string='Diario para facturas sin asiento', copy=False)