# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo.tools.float_utils import float_round, float_is_zero
from datetime import datetime
from dateutil import relativedelta
from werkzeug.urls import url_encode
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    as_type_action = fields.Many2one("as.stock.account.action",string='Tipo Acción',store=True)
    as_move_acion = fields.Many2one("account.move",string='Asiento de acción',store=True)

    def button_validate(self):
        res = super().button_validate()
        if self.state == 'done' and self.as_type_action:
            monto_cost = 0.0
            monto_sale = 0.0
            for line in self.move_ids_without_package:
                monto_cost += line.product_uom_qty * abs(line.price_unit)
                monto_sale += line.sale_line_id.as_subtotal_converter(line.product_uom_qty)
            if monto_cost <= 0.0:
                raise UserError(_("No se puede generar asiento de retorno con costo en Cero."))
            if monto_sale <= 0.0:
                raise UserError(_("No se puede generar asiento de retorno con precio de venta en Cero."))
            if monto_sale >= monto_cost:
                move = self.as_type_action.as_code_struct
            else:
                move = self.as_type_action.as_code_cost

            if move:
                self.as_move_acion =  move.as_get_account(self)
                if not self.as_move_acion:
                    raise UserError(_("Asiento no generado verifique estructura."))
            else:
                raise UserError(_("No esta creada la estructura contable de codigo "+str(self.as_type_action.as_code_struct)+" para asiento de piezas."))
        return res
    

class StockMove(models.Model):
    _inherit = "stock.move"

    as_subtotal = fields.Float(string="Subtotal")

    @api.depends('price_unit','product_uom_qty','quantity_done')
    @api.onchange('price_unit','product_uom_qty','quantity_done')
    def as_get_subtotal(self):
        for line in self:
            line.as_subtotal = line.price_unit*line.quantity_done

class StockAction(models.Model):
    _name = "as.stock.account.action"

    name = fields.Char(string="Numeracion Importacion")
    as_code_struct = fields.Many2one('as.account.structure', 'Código de estructura Precio de venta mayor a costo')
    as_code_cost = fields.Many2one('as.account.structure', 'Código de estructura Costo mayor a Precio de venta')