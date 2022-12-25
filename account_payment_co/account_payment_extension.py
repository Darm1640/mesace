# -*- encoding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                    All Rights Reserved.Jordi Esteve <jesteve@zikzakmedia.com>
# AvanzOSC, Avanzed Open Source Consulting
# Copyright (C) 2011-2012 Iker Coranti (www.avanzosc.com). All Rights Reserved
# Copyright (C) 2013 Akretion Ltda ME (www.akretion.com) All Rights Reserved
# Renato Lima <renato.lima@akretion.com.br>
# $Id$
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _


class payment_type(models.Model):
    _name = 'payment.type'
    _description = 'Payment type'
    name = fields.Char('Nombre', size=64, required=True,
            help='Nombre del tipo de pago', translate=True),
    code = fields.Char('Código', size=64, required=False,
            help='Especifica el código del tipo de pago'),
    active = fields.Boolean('Active', ),
    note = fields.Text('Descripción',
            help="""Descripción del tipo de pago"""),
    company_id = fields.Many2one('res.company', 'Compañía', required=True),


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    code_trans = fields.Char('Código transacción', size=64,
            help='Código de la transaccion que se registra en el banco destino')
    tipo_cta = fields.Char('Tipo cuenta', size=64,
            help='Carácter que identifica el tipo de cuenta en el banco. Ahorro=D Corriente=S')    
    concepto = fields.Char('Concepto', size=64,
            help='Información adicional que se requiera en el archivo plano del banco')
    referencia = fields.Char('Referencia', size=64,
            help='Información adicional que se requiera en el archivo plano del banco')     

class account_voucher(models.Model):
    _inherit = 'account.payment'

    payment_type = fields.Many2one('payment.type', 'Tipo de pago', required=True)
    epago = fields.Boolean('Pago electrónico' )
