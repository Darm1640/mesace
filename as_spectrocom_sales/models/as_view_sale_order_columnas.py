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

class SaleOrder(models.Model):
    _inherit = "sale.order"
    as_dato_factura = fields.Char(string="Nro Factura", compute="obtener_nombre_factura") 
    as_forma_pago_id = fields.Char(string='Forma de Pago')
    # as_pagos = fields.Float(string="Pagos", compute="ajustar_saldos") 
    # as_saldo = fields.Float(string='Saldo', compute="ajustar_saldos")
    
    
    # @api.depends('amount_total')
    # def _compute_saldo(self):
    #     for order in self:
    #         order.ajustar_saldos(True)
  
    
    def obtener_nombre_factura(self):
        for order in self:
            nombre=''
            invoices = self.env['account.move'].sudo().search([('invoice_origin', '=', order.name)])
            if invoices:
                for invoice in invoices:
                    payments = self.env['account.move'].sudo().search([('id', '=', invoice.id)])
                    for payment in payments:
                        if payment.name:
                            nombre+=str(payment.name)
                    
            order.as_dato_factura=nombre
        return True
    # def ajustar_saldos(self):
    #     for order in self:
    #         diario=0.0
    #         total_saldo = 0.0
    #         invoices = self.env['account.move'].sudo().search([('invoice_origin', '=', order.name)])
    #         if invoices:
    #             for invoice in invoices:
                    
    #                 payments = self.env['account.move'].sudo().search([('id', '=', invoice.id)])
    #                 for payment in payments.get_payment():
    #                     if payment.currency_id.name == 'USD':
    #                         diario+=round((payment.amount/0.143678000000),1)
    #                     else:
    #                         diario+=payment.amount
                    
    #                 total_saldo = invoice.amount_residual
    #                 self.env.cr.execute('UPDATE sale_order SET as_pagos='+str(diario)+' , as_saldo='+str(total_saldo)+' WHERE id='+str(order.id))
    #         order.as_pagos=diario
    #         order.as_saldo=total_saldo  
    #     return True
    
    # def stat_pagos(self):
    #     self.ajustar_saldos(False)

    
    # def stat_saldo(self):
    #     self.ajustar_saldos(False)

    def _obtener_dato_factura(self):
        as_dato_factura = ''
        dato = self.env['account.move'].sudo().search([('name', '=', self.name)], limit=1)
        #_logger.debug("\n\n\n\nDATO FACTURA... %s\n\n\n\n",dato)
        if dato:
            as_dato_factura = dato
        return as_dato_factura