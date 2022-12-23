# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import calendar
import time
from dateutil.relativedelta import relativedelta
import json
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('invoice_line_ids')
    def _compute_discount(self):
        for inv in self:
            amount_discount = 0.0
            for line in inv.invoice_line_ids:
                if line.as_discount_amount > 0:
                    amount_discount += line.as_discount_amount
                elif line.discount > 0:
                    line_discount_price_unit = line.price_unit * (line.discount / 100.0)
                    subtotal = round(line.quantity * line_discount_price_unit,2)
                    amount_discount += subtotal
            inv.as_amount_discount = amount_discount

    as_amount_discount = fields.Float('Monto Descuento',store=True)

    def _compute_discount_line(self):
        for inv in self:
            amount_discount = 0.0
            for line in inv.invoice_line_ids:
                if line.as_discount_amount > 0:
                    amount_discount += line.as_discount_amount
                elif line.discount > 0:
                    line_discount_price_unit = line.price_unit * (line.discount / 100.0)
                    subtotal = round(line.quantity * line_discount_price_unit,2)
                    amount_discount += subtotal
            return amount_discount

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.as_amount_discount = res._compute_discount_line()
        if res.as_amount_discount > 0:
            res.line_ids -= res.line_ids.filtered("global_discount_item")
            res._recompute_global_discount_lines_dict()
        return res

    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     for inv in self:
    #         if inv.as_amount_discount > 0:
    #             inv._recompute_global_discount_lines()
    #     return res
    
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        res = super()._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
        self.line_ids -= self.line_ids.filtered("global_discount_item")
        self.as_amount_discount = self._compute_discount_line()
        if self.as_amount_discount > 0:
            self._recompute_global_discount_lines()
        return res

    def _recompute_global_discount_lines(self):
        self.ensure_one()
        in_draft_mode = self != self._origin
        model = "account.move.line"
        create_method = in_draft_mode and self.env[model].with_context(check_move_validity=False).new or self.env[model].with_context(check_move_validity=False).create
        descuentos_model = self.env['as.global.discount'].sudo()
        descuentos = False
        if self.move_type == 'in_invoice':
            descuentos = descuentos_model.search([('discount_scope','=','discount_purchase')])
        elif self.move_type == 'out_invoice':
            descuentos = descuentos_model.search([('discount_scope','=','discount_sale')])
        if descuentos:
            for discount in descuentos:
                sign = -1 if self.move_type in {"in_invoice", "out_refund"} else 1
                self.as_amount_discount = self._compute_discount_line()
                disc_amount = sign * (self.as_amount_discount*(discount.discount/100))
                disc_amount = round(disc_amount,2)
                create_method(
                    {
                        "global_discount_item": True,
                        "move_id": self.id,
                        "name": "%s"
                        % (discount.name),
                        "debit": disc_amount > 0.0 and disc_amount or 0.0,
                        "credit": disc_amount < 0.0 and -disc_amount or 0.0,
                        "amount_currency": (disc_amount > 0.0 and disc_amount or 0.0)
                        - (disc_amount < 0.0 and -disc_amount or 0.0),
                        "account_id": discount.account_id.id,
                        "analytic_account_id": discount.account_analytic_id.id,
                        "exclude_from_invoice_tab": True,
                        "tax_ids": [],
                        "partner_id": self.commercial_partner_id.id,
                    }
                )
        if self.move_type == 'in_invoice':
            descuentos = descuentos_model.search([('discount_scope','=','discount_purchase_line')])
        elif self.move_type == 'out_invoice':
            descuentos = descuentos_model.search([('discount_scope','=','discount_sale_line')])
        if descuentos:
            for discount in descuentos:
                for line_inv in self.invoice_line_ids.filtered(lambda x: not x.exclude_from_invoice_tab):
                    sign = -1 if self.move_type in {"in_invoice", "out_refund"} else 1
                    self.as_amount_discount = self._compute_discount_line()
                    disc_amount = sign * (line_inv.as_discount_amount*(discount.discount/100))
                    disc_amount = round(disc_amount,2)
                    create_method(
                        {
                            "global_discount_item": True,
                            "move_id": self.id,
                            "name": "%s"
                            % (discount.name),
                            "debit": disc_amount > 0.0 and disc_amount or 0.0,
                            "credit": disc_amount < 0.0 and -disc_amount or 0.0,
                            "amount_currency": (disc_amount > 0.0 and disc_amount or 0.0)
                            - (disc_amount < 0.0 and -disc_amount or 0.0),
                            "account_id": line_inv.account_id.id,
                            "analytic_account_id": discount.account_analytic_id.id,
                            "exclude_from_invoice_tab": True,
                            "tax_ids": [],
                            "partner_id": self.commercial_partner_id.id,
                        }
                    )

    def _recompute_global_discount_lines_dict(self):
        self.ensure_one()
        in_draft_mode = self != self._origin
        line_dict = []
        account_line_obj = self.env['account.move.line']
        model = "account.move.line"
        create_method = in_draft_mode and self.env[model].with_context(check_move_validity=False).new or self.env[model].with_context(check_move_validity=False).create
        if self.move_type == 'in_invoice':
            descuentos = self.env['as.global.discount'].sudo().search([('discount_scope','=','discount_purchase')])
        elif self.move_type == 'out_invoice':
            descuentos = self.env['as.global.discount'].sudo().search([('discount_scope','=','discount_sale')])

        for discount in descuentos:
            sign = -1 if self.move_type in {"in_invoice", "out_refund"} else 1
            # self.as_amount_discount = self._compute_discount_line()
            disc_amount = sign * (self.as_amount_discount*(discount.discount/100))
            disc_amount = round(disc_amount,2)
            vals = {
                    "global_discount_item": True,
                    "move_id": self.id,
                    "name": "%s"
                    % (discount.name),
                    "debit": disc_amount > 0.0 and disc_amount or 0.0,
                    "credit": disc_amount < 0.0 and -disc_amount or 0.0,
                    "amount_currency": (disc_amount > 0.0 and disc_amount or 0.0)
                    - (disc_amount < 0.0 and -disc_amount or 0.0),
                    "account_id": discount.account_id.id,
                    "analytic_account_id": discount.account_analytic_id.id,
                    "exclude_from_invoice_tab": True,
                    "tax_ids": [],
                    "partner_id": self.commercial_partner_id.id,
                }
            line_dict.append(vals)
        if self.move_type == 'in_invoice':
            descuentos_line = self.env['as.global.discount'].sudo().search([('discount_scope','=','discount_purchase_line')])
        elif self.move_type == 'out_invoice':
            descuentos_line = self.env['as.global.discount'].sudo().search([('discount_scope','=','discount_sale_line')])

        for discount in descuentos_line:
            for line_inv in self.invoice_line_ids.filtered(lambda x: not x.exclude_from_invoice_tab):
                sign = -1 if self.move_type in {"in_invoice", "out_refund"} else 1
                # self.as_amount_discount = self._compute_discount_line()
                disc_amount = sign * (line_inv.as_discount_amount*(discount.discount/100))
                disc_amount = round(disc_amount,2)
                vals = {
                        "global_discount_item": True,
                        "move_id": self.id,
                        "name": "%s"
                        % (discount.name),
                        "debit": disc_amount > 0.0 and disc_amount or 0.0,
                        "credit": disc_amount < 0.0 and -disc_amount or 0.0,
                        "amount_currency": (disc_amount > 0.0 and disc_amount or 0.0)
                        - (disc_amount < 0.0 and -disc_amount or 0.0),
                        "account_id": line_inv.account_id.id,
                        "analytic_account_id": discount.account_analytic_id.id,
                        "exclude_from_invoice_tab": True,
                        "tax_ids": [],
                        "partner_id": self.commercial_partner_id.id,
                    }
                line_dict.append(vals)
        sum_credit = 0.00
        sum_debit = 0.00
        cont_d=0
        cont_c=0
        cont =0
        for line in line_dict:
            sum_credit += line['credit']
            sum_debit += line['debit']
            if line['credit'] > 0:
                cont_c=cont
            if line['debit'] > 0:
                cont_d=cont
            cont+=1
        total = sum_debit-sum_credit
        if total > 0.00:
            line_dict[cont_c]['credit']+= abs(total)
        if total < 0.00:
            line_dict[cont_d]['debit']+= abs(total)
        account_line_obj.with_context(check_move_validity=False).create(line_dict)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    global_discount_item = fields.Boolean()
