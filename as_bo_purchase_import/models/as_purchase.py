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
class asPurchase(models.Model):
    _inherit = 'purchase.order'

    as_importacion = fields.Boolean(string="Es Importación")
    as_cost_id = fields.Many2one('stock.landed.cost',string='Gasto de Importacion',copy=False)
    purchase_template_id = fields.Many2one('stock.landed.template', 'Plantilla de Gasto de envio')

    @api.onchange('as_importacion','order_line')
    def as_quitar_impuesto(self):
        if self.as_importacion == True:
            for line in self.order_line:
                # line.update({
                #     'taxes_id':'',
                # })
                line.taxes_id = None

    # @api.multi
    def button_confirm(self):
        res = super(asPurchase, self).button_confirm()
        if self.as_importacion == True and self.as_cost_id:
            if self.as_cost_id:
                self.as_cost_id.compute_landed_cost()
                if self.as_cost_id.state == 'draft':
                    self.as_cost_id.button_validate()
        return res

    # @api.multi
    def button_cancel_compra(self):
        res = super(asPurchase, self).button_cancel_compra()
        if self.as_importacion == True and self.as_cost_id:
            if self.as_cost_id:
                for cost in self.as_cost_id.cost_lines:
                    if cost.as_invoice_id:
                        if cost.as_invoice_id.state !='cancel':
                            cost.as_invoice_id.action_invoice_cancel()
                        cost.write({'as_invoice_id':''})
                self.as_cost_id.valuation_adjustment_lines.unlink()
                self.as_cost_id.as_valuation_summary_lines.unlink()
                self.as_cost_id.button_draft()
                self.as_cost_id=False
        return res
    
    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'invoice_date':self.date_order,
        }
        return invoice_vals

    # @api.multi
    def update_fixed_import(self,product_id,price,moneda):
        utilidad_edit=0.00
        #calculo de precio de acuerdo a la moneda seleccionada
        product_pricelist= self.env['product.pricelist.item'].search([('product_tmpl_id','=',product_id.product_tmpl_id.id)])
        currency_default = self.env.user.company_id.currency_id    
        price = currency_default._compute(moneda,currency_default,price)
        #en caso de que actualice PV
        if product_pricelist: #si el producto tiene tarifa
            for pricelist in product_pricelist:
                utilidad=(pricelist.as_utility_pricelist/100)
                pricelist.update({
                    'fixed_price':((price*(1+utilidad)/0.87)),
                })
        else: #si el producto no tiene tarifa
            utilidad=(product_id.as_product_utility/100)
            product_id.update({
                'list_price': ((price*(1+utilidad)/0.87)),
            })
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    as_cost_import = fields.Float(string="Costo Import.")
    as_importacion = fields.Boolean(related="order_id.as_importacion",store=True)

    # @api.multi
    def convert_amount_line_bruto(self,currency_default,currency_converter):
        if currency_default != currency_converter:
            return self.price_unit * currency_converter.rate
        else:
            return self.price_unit

    @api.onchange('as_cost_import')
    def cumpute_price_unit_p(self):
        if self.product_qty > 0:
            self.price_unit = self.as_cost_import / self.product_qty

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': self.id,
            'asset_category_id':self.product_id.asset_category_id.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res

    # @api.onchange('product_id','price_unit','product_qty')
    # # @api.multi
    # def _get_price_import(self):
    #     currency_default= self.env.user.company_id.currency_id
    #     for cost in self:
    #         if cost.as_importacion == True and self.user_has_groups('as_purchase_import.group_purchase_import_template'):
    #             total_qty = 0.0
    #             total_cost = 0.0
    #             total_weight = 0.0
    #             total_volume = 0.0
    #             total_line = 0.0
    #             all_val_line_values = cost.get_valuation_lines()
    #             for val_line_values in all_val_line_values:
    #                 weight= val_line_values['weight']
    #                 quantity= val_line_values['quantity']
    #                 former_cost= val_line_values['former_cost']
    #                 former_cost_fob= val_line_values['former_cost_fob']
    #                 volume= val_line_values['volume']
    #                 ttweight = val_line_values['tweight']
    #                 ttquantity = val_line_values['tquantity']
    #                 ttformer_cost = val_line_values['tformer_cost']
    #                 ttformer_cost_fob = val_line_values['tformer_cost_fob']
    #                 ttvolume = val_line_values['tvolume']
    #                 tweight = 0.00
    #                 tquantity = 0.00
    #                 tformer_cost = 0.00
    #                 tvolume = 0.00
    #                 val_line_head={}
    #                 val_line={}
    #                 total_line += 1
    #                 if not cost.order_id.purchase_template_id:
    #                     raise UserError(_("Por favor se necesita seleccionar una plantilla"))
    #                 for cost_line in cost.order_id.purchase_template_id.template_cost_lines:
    #                     price_line = cost_line.price_unit
    #                     if cost_line.as_facturado==True:
    #                         price_line= (cost_line.price_unit*87)/100
    #                     val_line_head = {
    #                         'cost_line_id': cost_line.id,
    #                         'product_id': val_line_values['product_id'],
    #                         'line_id': val_line_values['line_id'],
    #                         'move_id': val_line_values['move_id'],
    #                         }
    #                     if cost_line.split_method == 'by_quantity' and ttquantity > 0.00:
    #                         val_line = {
    #                             'quantity': price_line * (quantity/ttquantity),
    #                             'weight': 0.00,
    #                             'volume': 0.00,
    #                             'former_cost': 0.00,
    #                             }
    #                         val_line.update(val_line_head)
    #                         tquantity += price_line * (quantity/ttquantity)
    #                     elif cost_line.split_method == 'by_weight' and ttweight > 0.00:
    #                         val_line = {
    #                             'weight': price_line * (weight/ttweight),
    #                             'quantity': 0.00,
    #                             'volume': 0.00,
    #                             'former_cost': 0.00,
    #                             }
    #                         val_line.update(val_line_head)
    #                         tweight+= price_line * (weight/ttweight)
    #                     elif cost_line.split_method == 'by_volume' and ttvolume > 0.00:
    #                         val_line = {
    #                             'volume': price_line * (volume/ttvolume),
    #                             'quantity': 0.00,
    #                             'weight': 0.00,
    #                             'former_cost': 0.00,
    #                             }
    #                         val_line.update(val_line_head)
                            
    #                         tvolume += price_line * (volume/ttvolume)
    #                     elif cost_line.split_method == 'by_current_cost_price' and ttformer_cost_fob>0.00:
    #                         val_line = {
    #                             'former_cost': price_line * (former_cost_fob/ttformer_cost_fob),
    #                             'quantity': 0.00,
    #                             'volume': 0.00,
    #                             'weight': 0.00,
    #                             }
    #                         val_line.update(val_line_head)
    #                         tformer_cost += price_line * (former_cost_fob/ttformer_cost_fob)
    #                     elif cost_line.split_method == 'equal':
    #                         val_line = {
    #                             'former_cost_per_unit': (line.price_unit / total_line),
    #                             'quantity': 0.00,
    #                             'volume': 0.00,
    #                             'former_cost': 0.00,
    #                             }
    #                         val_line.update(val_line_head)
    #                     else:
    #                         raise UserError(_("Por favor revise la configuracion de los productos si es peso y volumen no puden estar en cero"))
    #                 value = tweight+tquantity+tformer_cost+tvolume
    #                 sum_todo= round(value,2)
    #                 currency_default= cost.env.user.company_id.currency_id
    #                 currency_converter= cost.order_id.currency_id
    #                 price_unit= cost.convert_amount_line_bruto(currency_default,currency_converter,cost.price_unit)
    #                 cost.as_cost_import = price_unit + (sum_todo / cost.product_qty)#nuevo costo
                    

    #toma los valores de las lineas de costo
    def get_valuation_lines(self):
        lines = []
        #usando factores para el calculo de totales
        total_qty = 0.00
        total_weight = 0.00
        total_volume = 0.00
        former_cost= 0.00
        former_cost_fob = 0.00
        #se totalizan para el calculo del factor
        currency_default= self.env.user.company_id.currency_id
        for val_line_values in self:
            currency_converter= val_line_values.order_id.currency_id
            price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,val_line_values.price_unit)
            total_qty += val_line_values.product_qty
            total_weight += val_line_values.product_id.weight
            total_volume += val_line_values.product_id.volume
            former_cost += price_unit
            former_cost_fob += price_unit * val_line_values.product_qty

        for line in self:
            currency_converter= line.order_id.currency_id
            price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line.price_unit)
            
            vals = {
                'product_id': line.product_id.id,
                'line_id': line.id,
                'move_id': 0,
                'quantity': (line.product_qty),
                'tquantity': (total_qty),
                'former_cost': (price_unit),
                'tformer_cost': (former_cost),
                'former_cost_fob': (price_unit*line.product_qty),
                'tformer_cost_fob': (former_cost_fob),
                'weight': (line.product_id.weight),
                'tweight': (total_weight),
                'volume': (line.product_id.volume),
                'tvolume': (total_volume),
            }
            lines.append(vals)

        if not lines and self.order_id:
            raise UserError(_("No puede aplicar costos de aterrizaje en las transferencias elegidas. Los costos de aterrizaje solo se pueden aplicar para productos con valuación de inventario automatizada"))

        return lines

    # @api.multi
    def convert_amount_line_bruto(self,currency_default,currency_converter,amount):
        if currency_default != currency_converter:
            digits = dp.get_precision('Product Price')(self._cr)
            return currency_converter._convert(amount,currency_default, self.company_id, self.date_order,round=False)
        else:
            return amount