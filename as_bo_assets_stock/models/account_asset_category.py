from odoo import api, models, fields
from odoo import tools

class product_product(models.Model):
    _inherit = 'account.asset.category'

    as_sequence_id = fields.Many2one('ir.sequence', 'Secuencia código',copy=False)