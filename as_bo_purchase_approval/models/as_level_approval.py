from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = 'as.level.approval'
    _description = "Modelo para guardar los niveles de aprobacion de compras a usuarios"

    as_users_ids = fields.Many2many('res.users', string="Usuario(s) Aprobador")
    as_amount_min = fields.Float('Monto Minimo')
    as_amount_max = fields.Float('Monto Maximo')
    as_type = fields.Selection(selection=[
            ('purchase', 'Compras'),
            ('viatico', 'Viaticos'),
            ('viajes', 'Viajes'),
        ], string='Tipo', required=True, default='purchase')

