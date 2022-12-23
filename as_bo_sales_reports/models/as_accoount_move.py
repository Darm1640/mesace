
# -*- coding: utf-8 -*-
from datetime import datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, ormcache
import logging
import json
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit="account.move"
    def get_sale(self):
        sale = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        return sale
    
    def get_payment(self):
        payment = {}
        account_payment = self.env['account.payment']
        if json.loads(self.invoice_payments_widget):
            payment = json.loads(self.invoice_payments_widget)
            for payment_inv in payment['content']:
                payment_id = int(payment_inv['account_payment_id'])
                account_payment |=self.env['account.payment'].search([('id','=',payment_id),('state','=','posted')])
        return account_payment
    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'nit' : self.env.user.company_id.vat or '',
            'direccion1' : self.env.user.company_id.street or '',
            'sucursal' : self.env.user.company_id.city or '',
            'telefono' : self.env.user.company_id.phone or '',
            'ciudad' : self.env.user.company_id.city or '',
            'pais' : self.env.user.company_id.country_id.name or '',
        }
        info = diccionario_dosificacion[str(requerido)]
        return info
