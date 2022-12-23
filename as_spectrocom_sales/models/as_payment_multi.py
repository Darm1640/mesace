# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, SU, SA
_logger = logging.getLogger(__name__)


class AsPaymentMulti(models.Model):
    _inherit = 'as.payment.multi'

    def get_sales_deuda_ventas(self):
        sales_ids = []
        cont = 0
        total = self.as_amount
        self.as_sale_ids.unlink()
        # if self.as_amount <= 0:
        #     raise UserError(_("Amount can't be negative or zero !"))
        if self.as_partner_id.id:
            consulta = "SELECT\
                            ai.id,ai.as_saldo,ai.name,ai.name,to_char(ai.date_order, 'YYYY-MM-DD'),pp.currency_id\
                            FROM sale_order AS ai\
                            join product_pricelist AS pp on pp.id=ai.pricelist_id\
                            WHERE ai.as_saldo > 1.5 \
                            AND ai.state in ('autotizada') and ai.partner_id = %s order by ai.date_order asc"
            self.env.cr.execute(consulta,[(self.as_partner_id.id)])
            amount = self.as_amount
            for invoice in self.env.cr.fetchall():
                currency_sale = self.env['res.currency'].search([('id','=', invoice[5])])
                amount_total = currency_sale._convert(invoice[1],self.currency_id,self.env.user.company_id, self.date,round=False)
                if amount > 0:
                    if float(amount_total) >= float(amount):
                        amount = float(amount_total)
                    else:
                        amount = amount - float(amount_total)
                vals = { 
                    'name':invoice[3],
                    'date':invoice[4],
                    'as_sale_id' : invoice[0],
                    'as_amount_total' : amount_total,
                }
                line_id = self.env['as.payment.multi.line'].create(vals)
                sales_ids.append(line_id.id)
                cont+=1
            self.as_sale_ids = sales_ids
            if self.as_amount != 0.0:
                for datos in self:
                    amount_total = 0.00
                    for linet in datos.as_sale_ids:
                        amount_total += linet.as_amount_total
                    if datos.as_amount > amount_total:
                        datos.as_amount = amount_total
                    currency_default = datos.env.user.company_id.currency_id
                    currency_trans = datos.as_partner_id.currency_id
                    monto = self._conertir_moneda(currency_default,currency_trans,datos.as_amount,datos.date)
                    for line in datos.as_sale_ids:
                        moneda = datos.currency_id.name
                        line.currency_id = datos.currency_id
                        if monto >= line.as_amount_total:
                            line.as_amount = line.as_amount_total
                            monto -= round(line.as_amount_total,2)
                        elif monto > 0:
                            line.as_amount = round(monto,2)
                            monto = 0
                        else: line.as_amount = 0.0
            # if cont > 0 and total > 0 and not self.as_is_anticipo:
            #     diferencia = total - self.as_amount
            #     self.as_amount = total
            #     self.as_sale_ids[cont-1].as_amount= self.as_sale_ids[cont-1].as_amount + round(diferencia,2)
        self.state = 'data'
