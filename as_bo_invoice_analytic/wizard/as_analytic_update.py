# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError
import re
import xlrd
from xlrd import open_workbook
import base64
import logging
_logger = logging.getLogger(__name__)

class as_update_analytic(models.Model):
    _name="as.analytic.update"
    _description="Modulo para actualizar cuentas analiticas"

    as_lines_ids = fields.Many2many('as.analytic.update.line', string='Lineas de Factura')

    @api.model
    def default_get(self, fields):
        res = super(as_update_analytic, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        dictline = []
        dictlinestock = []
        stock = 1
        menor = 0.0
        value = 0.0
        if res_ids and res_ids[0]:
            so_line = res_ids[0]
            so_line_obj = self.env['account.move'].browse(so_line)
            for line in so_line_obj.invoice_line_ids:
                vals = {
                    'as_move_line': line.id,
                }
                dictlinestock.append([0, 0, vals])
           
            res.update({
                'as_lines_ids':dictlinestock,
            })
        return res


    def generar_updates(self):
        for line in self.as_lines_ids:
            line.as_move_line.analytic_account_id = line.as_analytic_account_id
        return True
        

class as_importar_productos(models.Model):
    _name="as.analytic.update.line"
    _description="Modulo para actualizar cuentas analiticas lineas"

    as_move_line = fields.Many2one('account.move.line', string='Linea Factura')
    as_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')