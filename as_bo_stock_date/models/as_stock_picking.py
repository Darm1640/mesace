from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import uuid

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    date = fields.Datetime('Fecha Creación', default=fields.Datetime.now, index=True, track_visibility='onchange',states={'cancel': [('readonly', True)]},help="Creation Date, usually the time of the order")

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        self.get_replicar_date_to_move()
        return res

    @api.onchange('date')
    def get_replicar_date_to_move(self):
        for pick in self:
            for move in pick.move_lines:
                move.date=pick.date
            for move in pick.move_ids_without_package:
                move.date=pick.date
