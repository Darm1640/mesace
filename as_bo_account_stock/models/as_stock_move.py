# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, OrderedSet

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        cost = abs(cost)
        account_line_obj = self.env['account.move.line']
        if not self.picking_id.as_account_move:
            AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
            move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
            if move_lines:
                if self.picking_id and self.picking_id.date:
                    date = self.picking_id.date.strftime('%Y-%m-%d')
                else:
                    date = self._context.get('force_period_date', fields.Date.context_today(self))
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': description,
                    'stock_move_id': self.id,
                    'stock_valuation_layer_ids': [(6, None, [svl_id])],
                    'move_type': 'entry',
                })
                self.picking_id.as_account_move = new_account_move
                # new_account_move._post()
        else:
            AccountMove = self.picking_id.as_account_move.with_context(default_journal_id=journal_id)
            move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
            for line in move_lines:
                line[2]['move_id'] = self.picking_id.as_account_move.id
                account_line_obj.with_context(check_move_validity=False,move_id=self.picking_id.as_account_move.id).create(line[2])



class StockMove(models.Model):
    _inherit = "stock.picking"

    as_account_move = fields.Many2one('account.move', string="Asiento Contable",copy=False)

    def button_validate(self):
        res = super().button_validate()
        for pick in self:
            if pick.as_account_move:
                pick.as_account_move._post()
        return res