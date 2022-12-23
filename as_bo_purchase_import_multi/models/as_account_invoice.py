# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
#Generacion del QR
import qrcode
import tempfile
import base64
#Convertir numeros en texto
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time
from time import mktime
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
class AccountInvoice(models.Model):
    _inherit = 'account.move'

    as_import_fiscal = fields.Boolean(string="Import Fiscal")


    # @api.model
    # def invoice_line_move_line_get(self):
    #     res = []
    #     monto_total =0.0
    #     retenciones = self.env['as.tipo.retencion'].search([('id','=',self.as_tipo_retencion.id)])
    #     sin_retencion = self.env['as.tipo.retencion'].search([('as_iue', '=', 0),('as_it', '=', 0),('as_iva', '=', 0)],limit=1)
    #     for line in self.invoice_line_ids:
    #         if not line.account_id:
    #             continue
    #         if line.quantity==0:
    #             continue
    #         tax_ids = []
    #         for tax in line.invoice_line_tax_ids:
    #             tax_ids.append((4, tax.id, None))
    #             for child in tax.children_tax_ids:
    #                 if child.type_tax_use != 'none':
    #                     tax_ids.append((4, child.id, None))
    #         analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
    #         if 'as_importacion' in line.purchase_line_id.order_id:
    #             if line.purchase_line_id.order_id.as_importacion == True:
    #                 move_line_dict = {
    #                 'invl_id': line.id,
    #                 'type': 'src',
    #                 'name': line.name,
    #                 'price_unit': line.price_unit,
    #                 'quantity': line.quantity,
    #                 'price': line.price_subtotal,
    #                 'account_id': line.purchase_line_id.product_id.property_account_import_id.id,
    #                 'product_id': line.product_id.id,
    #                 'uom_id': line.uom_id.id,
    #                 'account_analytic_id': line.account_analytic_id.id,
    #                 'analytic_tag_ids': analytic_tag_ids,
    #                 'tax_ids': tax_ids,
    #                 'invoice_id': self.id,
    #                 }
    #             else:
    #                 if line.invoice_id.type == "out_invoice":
    #                     move_line_dict = {
    #                     'invl_id': line.id,
    #                     'type': 'src',
    #                     'name': line.name,
    #                     'price_unit': line.price_unit,
    #                     'quantity': line.quantity,
    #                     'price': (line.price_unit * line.quantity)*0.87,
    #                     'account_id': line.account_id.id,
    #                     'product_id': line.product_id.id,
    #                     'uom_id': line.uom_id.id,
    #                     'account_analytic_id': line.account_analytic_id.id,
    #                     'analytic_tag_ids': analytic_tag_ids,
    #                     'tax_ids': [],
    #                     'invoice_id': self.id,
    #                     }
    #                 else:
    #                     if self.as_tipo_retencion == sin_retencion or not self.as_tipo_retencion or self.as_tipo_retencion.as_gasto_fiscal:
    #                         move_line_dict = {
    #                         'invl_id': line.id,
    #                         'type': 'src',
    #                         'name': line.name,
    #                         'price_unit': line.price_unit,
    #                         'quantity': line.quantity,
    #                         'price': line.price_subtotal,
    #                         'account_id': line.account_id.id,
    #                         'product_id': line.product_id.id,
    #                         'uom_id': line.uom_id.id,
    #                         'account_analytic_id': line.account_analytic_id.id,
    #                         'analytic_tag_ids': analytic_tag_ids,
    #                         'tax_ids': tax_ids,
    #                         'invoice_id': self.id,
    #                         }
    #                     else:
    #                         total_prcentaje=0.0
    #                         total_prcentaje = retenciones.as_iue+retenciones.as_it+retenciones.as_iva
    #                         monto_total += (line.price_subtotal)/(1-(total_prcentaje/100))
    #                         if total_prcentaje > 0:
    #                             move_line_dict = {
    #                             'invl_id': line.id,
    #                             'type': 'src',
    #                             'name': line.name,
    #                             'price_unit': line.price_unit,
    #                             'quantity': line.quantity,
    #                             'price': (line.price_subtotal)/(1-(total_prcentaje/100)),
    #                             'account_id': line.account_id.id,
    #                             'product_id': line.product_id.id,
    #                             'uom_id': line.uom_id.id,
    #                             'account_analytic_id': line.account_analytic_id.id,
    #                             'analytic_tag_ids': analytic_tag_ids,
    #                             'tax_ids': tax_ids,
    #                             'invoice_id': self.id,
    #                             }
    #                         else:
    #                             raise UserError(_('La suma de los porcentajes de retencion es cero.'))
    #         else:
    #             if line.invoice_id.type == "out_invoice":
    #                 move_line_dict = {
    #                 'invl_id': line.id,
    #                 'type': 'src',
    #                 'name': line.name,
    #                 'price_unit': line.price_unit,
    #                 'quantity': line.quantity,
    #                 'price': (line.price_unit * line.quantity)*0.87,
    #                 'account_id': line.account_id.id,
    #                 'product_id': line.product_id.id,
    #                 'uom_id': line.uom_id.id,
    #                 'account_analytic_id': line.account_analytic_id.id,
    #                 'analytic_tag_ids': analytic_tag_ids,
    #                 'tax_ids': [],
    #                 'invoice_id': self.id,
    #                 }
    #             else:
    #                 move_line_dict = {
    #                 'invl_id': line.id,
    #                 'type': 'src',
    #                 'name': line.name,
    #                 'price_unit': line.price_unit,
    #                 'quantity': line.quantity,
    #                 'price': line.price_subtotal,
    #                 'account_id': line.account_id.id,
    #                 'product_id': line.product_id.id,
    #                 'uom_id': line.uom_id.id,
    #                 'account_analytic_id': line.account_analytic_id.id,
    #                 'analytic_tag_ids': analytic_tag_ids,
    #                 'tax_ids': tax_ids,
    #                 'invoice_id': self.id,
    #                 }
    #         res.append(move_line_dict)
    #     if self.type == "in_invoice":
    #         if self.as_tipo_retencion != sin_retencion:
    #             # IT linea
    #             if retenciones.as_it > 0.0:
    #                 monto_it = (monto_total*(retenciones.as_it/100))
    #                 move_line_dict = {
    #                     'type': 'src',
    #                     'name':'Retencion IT',
    #                     'price_unit':  -monto_it,
    #                     'quantity': 1,
    #                     'price': -monto_it,
    #                     'account_id': retenciones.as_cuenta_it.id,
    #                     'invoice_id': self.id,
    #                     }
    #                 res.append(move_line_dict)
    #             # IUE linea
    #             if retenciones.as_iue > 0.0:
    #                 monto_iue = (monto_total*(retenciones.as_iue/100))
    #                 move_line_dict = {
    #                     'type': 'src',
    #                     'name':'Retencion IUE',
    #                     'price_unit':  -monto_iue,
    #                     'quantity': 1,
    #                     'price':  -monto_iue,
    #                     'account_id': retenciones.as_cuenta_iue.id,
    #                     'invoice_id': self.id,
    #                     }
    #                 res.append(move_line_dict)
    #             # IVA linea
    #             if retenciones.as_iva > 0.0:
    #                 monto_iva = (monto_total*(retenciones.as_iva/100))
    #                 move_line_dict = {
    #                 'type': 'src',
    #                 'name':'Retencion IVA',
    #                 'price_unit':  -monto_iva,
    #                 'quantity': 1,
    #                 'price':  -monto_iva,
    #                 'account_id': retenciones.as_cuenta_iva.id,
    #                 'invoice_id': self.id,
    #                 }
    #                 res.append(move_line_dict)
    #     return res