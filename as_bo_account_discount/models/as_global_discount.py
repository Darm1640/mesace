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

class GlobalDiscount(models.Model):
    _name = "as.global.discount"
    _description = "Global Discount"
    _order = "sequence, id desc"

    sequence = fields.Integer(help="Secuencia")
    name = fields.Char(string="Nombre Descuento", required=True)
    discount = fields.Float(digits="descuento", required=True, default=0.0)
    discount_scope = fields.Selection(
        selection=[("sale", "Sales"), ("purchase", "Purchases"),("discount_purchase", "Descuento compra"),("discount_sale", "Descuento Ventas"),("discount_sale_line", "Descuento Ventas lineas"),("discount_purchase_line", "Descuento Compras lineas")],
        default="sale",
        required="True",
        string="Tipo Descuento",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañia",
        default=lambda self: self.env.company,
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta",
        domain="[('user_type_id.type', 'not in', ['receivable', 'payable'])]",
        check_company=True,
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Cuenta Analitica",
        check_company=True,
    )

    def _get_global_discount_vals(self, base, account_id=False, **kwargs):
        """Return account as well if passed"""
        res = super()._get_global_discount_vals(base)
        if account_id:
            res.update({"account_id": account_id})
        return res

    def name_get(self):
        result = []
        for one in self:
            result.append((one.id, "{} ({:.2f}%)".format(one.name, one.discount)))
        return result

    def _get_global_discount_vals(self, base, **kwargs):
        """Prepare the dict of values to create to obtain the discounted
         amount

        :param float base: the amount to discount
        :return: dict with the discounted amount
        """
        self.ensure_one()
        return {
            "global_discount": self,
            "base": base,
            "base_discounted": base * (1 - (self.discount / 100)),
        }

 