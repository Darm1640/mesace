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
#tools
from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_is_zero
import logging
_logger = logging.getLogger(__name__)

class AsLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    _description = 'As Stock Landed Cost'

    purchase_template_id = fields.Many2one('stock.landed.template', 'Plantilla de Gasto de envio')

    # @api.multi
    def _mostrar_fecha_pedido(self):
        editable = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_mostrar_fecha'))
        self.as_fecha_Editable =  editable
        return editable

    as_fecha_Editable = fields.Boolean(string='Mostrar fecha en reporte', compute='_mostrar_fecha_pedido',default='_mostrar_fecha_pedido')

    # @api.multi
    def get_price_unit(self,cost_line):
        if cost_line.as_facturado==True and cost_line.as_tipo_factura.as_costo_cero != True:
            price_line= (cost_line.price_unit*87)/100
        else:
            price_line= cost_line.price_unit
        return price_line    
    
    # @api.multi
    def get_price_unit_total(self):
        price_line = 0.0
        for cost_line in self.cost_lines:
            if cost_line.as_tipo_factura.as_no_participa:
                price_line += 0.0          
            elif cost_line.as_facturado==True and cost_line.as_tipo_factura.as_costo_cero != True:
                price_line += (cost_line.price_unit*87)/100
            else:
                price_line += cost_line.price_unit
        return price_line

    # @api.multi
    @api.onchange('purchase_template_id')
    def _get_cost_line_template(self):
        data = {}
        line_cost = [(5, 0, 0)]
        for lines in self.purchase_template_id.template_cost_lines:
            data = {
                'name': lines.name,
                'product_id' : lines.product_id.id,
                'price_unit': lines.price_unit,
                'split_method': lines.split_method,
                'account_id': lines.account_id.id,
                'template_cost_id': self.purchase_template_id.id,
            }
            line_cost.append((0, 0, data))
        self.cost_lines = line_cost

    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion= {}
        qr_code_id = self.env['qr.code'].search([('id', 'in', self.env['res.users'].browse(self._context.get('uid')).dosificaciones.ids),('activo', '=', True)],limit=1)
        if qr_code_id:
            diccionario_dosificacion = {
                'nombre_empresa' : qr_code_id.nombre_empresa or '',
                'nit' : qr_code_id.nit_empresa or '',
                'direccion1' : qr_code_id.direccion1 or '',
                'telefono' : qr_code_id.telefono or '',
                'ciudad' : qr_code_id.ciudad or '',
                'pais' : self.company_id.country_id.name or '',
                'actividad' : qr_code_id.descripcion_actividad or '',
                'sucursal' : qr_code_id.sucursal or '',
                'fechal' : qr_code_id.fecha_limite_emision or '',
            }
        else:
            diccionario_dosificacion = {
                'nombre_empresa' : self.company_id.name or '',
                'nit' : self.company_id.vat or '',
                'direccion1' : self.company_id.street or '',
                'telefono' : self.company_id.phone or '',
                'ciudad' : self.company_id.city or '',
                'sucursal' : self.company_id.city or '',
                'pais' : self.company_id.country_id.name or '',
                'actividad' :  self.company_id.name or '',
                'fechal' : self.company_id.phone or '',

            }
        info = diccionario_dosificacion[str(requerido)]
        return info

    # @api.multi
    def _purchase_available(self):
        purchase_with_cost= self.env['purchase.order'].sudo().search([('state', '=', 'purchase'),('as_importacion', '=', True)])
        ids_not=[]
        for purchase in purchase_with_cost:
            if not purchase.as_cost_id:
                ids_not.append(purchase.id)
        return [('id', 'in', tuple(ids_not))]

    # @api.multi
    def button_cancel(self):
        if any(cost.state == 'done' for cost in self):
            raise UserError(
                _('Validated landed costs cannot be cancelled, but you could create negative landed costs to reverse them'))
        return self.write({'state': 'cancel'})


    # @api.multi
    def _picking_available(self):
        picking_with_cost= self.env['stock.landed.cost'].sudo().search([('picking_id', '!=', '')])
        ids_not_picking=[]
        for cost in picking_with_cost:
            ids_not_picking.append(cost.purchase_id.id)
        return [('id', 'not in', tuple(ids_not_picking)),('state', '!=', 'done')]

    purchase_id = fields.Many2one('purchase.order', string='Pedido de Compra', copy=False, states={'done': [('readonly', True)]}, domain=_purchase_available)
    picking_id = fields.Many2one('stock.picking', string='Movimientos de Inventario', copy=False, states={'done': [('readonly', True)]},domain=_picking_available)
    amount_total_purchase = fields.Float('Total Compra',
        digits=0, track_visibility='always')
    amount_total_gasto = fields.Float('Total', compute='_compute_total_amount',
        digits=0, store=True, track_visibility='always')
    as_valuation_summary_lines = fields.One2many(
        'as.stock.valuation.summary.lines', 'cost_id', 'Resumen de Valoracion de linea de costo',
        states={'done': [('readonly', True)]})
    as_document_type = fields.Selection(
        selection=[('Ninguno','Ninguno'),
        ('compra','Compras'),
        ('inventario','Movimiento de Inventario')]
        ,default='Ninguno', string="Tipo Documento")
    as_calculado = fields.Boolean(string="Calculado", default=False)

    # @api.multi
    @api.onchange('cost_lines')
    def _verifica_calculo(self):
        cantidad= len(self.cost_lines)
        cont=0
        for line in self.cost_lines:
            if line.as_invoice_id:
                cont+=1
        if cantidad == cont:
            self.as_calculado = True
        else:
            self.as_calculado = False

    #trae el total de la compra
    @api.onchange('purchase_id')
    def onchange_amount_purchase(self):
        currency_default = self.env.user.company_id.currency_id
        currency_purchase = self.purchase_id.currency_id
        monto_compra = currency_default._compute(currency_purchase,currency_default,self.purchase_id.amount_total)
        self.amount_total_purchase= monto_compra
    #calcula la suma entre los gastos de envio y el monto d ela compra
    # @api.one
    @api.depends('cost_lines.price_unit','purchase_id')
    def _compute_total_amount(self):
        self.amount_total = sum(line.price_unit for line in self.cost_lines)
        self.amount_total_gasto = self.amount_total_purchase + self.amount_total

    #funcion heredada que calcula los montos d elas solapas
    @api.model
    def create(self, vals):
        res = super(AsLandedCost, self).create(vals)
        res.purchase_id.write({
            'as_cost_id':res.id
        })
        return res

    # @api.multi
    def write(self, vals):
        res = super(AsLandedCost, self).write(vals)
        self.purchase_id.write({
            'as_cost_id':self.id
        })
        return res
    #funcion heredada que calcula los montos d elas solapas
    # @api.multi
    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()
        digits = dp.get_precision('Product Price')
        towrite_dict = {}
        currency_default= self.env.user.company_id.currency_id
        if self.as_document_type=='compra':
            for cost in self.filtered(lambda cost: cost.purchase_id.order_line):
                total_qty = 0.0
                total_cost = 0.0
                total_weight = 0.0
                total_volume = 0.0
                total_line = 0.0
                all_val_line_values = cost.get_valuation_lines()
                for val_line_values in all_val_line_values:
                    weight= val_line_values['weight']
                    quantity= val_line_values['quantity']
                    former_cost= val_line_values['former_cost']
                    former_cost_fob= val_line_values['former_cost_fob']
                    volume= val_line_values['volume']
                    ttweight = val_line_values['tweight']
                    ttquantity = val_line_values['tquantity']
                    ttformer_cost = val_line_values['tformer_cost']
                    ttformer_cost_fob = val_line_values['tformer_cost_fob']
                    ttvolume = val_line_values['tvolume']
                    tweight = 0.00
                    tquantity = 0.00
                    tformer_cost = 0.00
                    tvolume = 0.00
                    val_line_head={}
                    val_line={}
                    total_line += 1
                    #excluimos lineas de IVA
                    lines_cost = self.env['stock.landed.cost.lines']
                    for line in cost.cost_lines:
                        if line.as_tipo_factura.as_no_participa != True:
                            lines_cost += line
                    for cost_line in lines_cost:
                        price_line = cost_line.price_unit
                        if cost_line.as_facturado==True and cost_line.as_tipo_factura.as_costo_cero != True:
                            price_line= (cost_line.price_unit*87)/100
                        val_line_head = {
                            'cost_id': cost.id, 
                            'cost_line_id': cost_line.id,
                            'product_id': val_line_values['product_id'],
                            'line_id': val_line_values['line_id'],
                            'move_id': val_line_values['move_id'],
                            }
                        if cost_line.split_method == 'by_quantity' and ttquantity > 0.00:
                            val_line = {
                                'quantity': price_line * (quantity/ttquantity),
                                'weight': 0.00,
                                'volume': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                            tquantity += price_line * (quantity/ttquantity)
                        elif cost_line.split_method == 'by_weight' and ttweight > 0.00:
                            val_line = {
                                'weight': price_line * (weight/ttweight),
                                'quantity': 0.00,
                                'volume': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                            tweight+= price_line * (weight/ttweight)
                        elif cost_line.split_method == 'by_volume' and ttvolume > 0.00:
                            val_line = {
                                'volume': price_line * (volume/ttvolume),
                                'quantity': 0.00,
                                'weight': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                            
                            tvolume += price_line * (volume/ttvolume)
                        elif cost_line.split_method == 'by_current_cost_price' and ttformer_cost_fob>0.00:
                            val_line = {
                                'former_cost': price_line * (former_cost_fob/ttformer_cost_fob),
                                'quantity': 0.00,
                                'volume': 0.00,
                                'weight': 0.00,
                                }
                            val_line.update(val_line_head)
                            tformer_cost += price_line * (former_cost_fob/ttformer_cost_fob)
                        elif cost_line.split_method == 'equal':
                            val_line = {
                                'former_cost': (line.price_unit / total_line),
                                'quantity': 0.00,
                                'volume': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                        else:
                            raise UserError(_("Por favor revise la configuracion de los productos si es peso y volumen no puden estar en cero"))
                        
                        self.env['stock.valuation.adjustment.lines'].create(val_line)
                    line_order = self.env['purchase.order.line'].sudo().search([('id', '=', val_line_values['line_id'])])
                    decimal_precision = self.env['decimal.precision'].precision_get(digits)
                    sum_todo= round(tweight+tquantity+tformer_cost+tvolume,decimal_precision)
                    currency_default= self.env.user.company_id.currency_id
                    currency_converter= line_order.order_id.currency_id
                    price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line_order.price_unit)
                    vals_summary = ({
                        'cost_id': cost.id, 
                        'move_id': val_line_values['move_id'],
                        'line_id': val_line_values['line_id'],
                        'product_id': val_line_values['product_id'],
                        'weight': line_order.product_id.weight,
                        'price_unit': price_unit, #precio unitario
                        'volume': line_order.product_id.volume, #volumen
                        'quantity': line_order.product_qty, #cantidad
                        'as_value_fob':  price_unit * line_order.product_qty, #valor FOB
                        'as_cost_fob': sum_todo, #costo total
                        'as_cost_total': (price_unit * line_order.product_qty)+sum_todo, #costo total
                        'as_cost_unit': sum_todo / line_order.product_qty,#costo unitario
                        'as_cost_new': price_unit + (sum_todo / line_order.product_qty),#nuevo costo
                    })
                    self.recalcular_costo(val_line_values['move_id'],(price_unit + (sum_todo / line_order.product_qty)))
                    summary= self.env['as.stock.valuation.summary.lines'].sudo().search([('cost_id', '=', cost.id),('line_id', '=', val_line_values['line_id'])])
                    if summary:
                        summary.update(vals_summary)
                    else:
                        self.env['as.stock.valuation.summary.lines'].create(vals_summary)
                    total_qty += val_line_values.get('quantity', 0.0)
                    total_weight += val_line_values.get('weight', 0.0)
                    total_volume += val_line_values.get('volume', 0.0)

                    former_cost = val_line_values.get('former_cost', 0.0)
                    total_cost += tools.float_round(former_cost, decimal_precision) if digits else former_cost

                    total_line += 1
                for line in cost.cost_lines:
                    value_split = 0.0
                    for valuation in cost.valuation_adjustment_lines:
                        value = 0.0
                        if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                            if line.split_method == 'by_quantity' and total_qty:
                                per_unit = (line.price_unit / total_qty)
                                value = valuation.quantity * per_unit
                            elif line.split_method == 'by_weight' and total_weight:
                                per_unit = (line.price_unit / total_weight)
                                value = valuation.weight * per_unit
                            elif line.split_method == 'by_volume' and total_volume:
                                per_unit = (line.price_unit / total_volume)
                                value = valuation.volume * per_unit
                            elif line.split_method == 'equal':
                                value = (line.price_unit / total_line)
                            elif line.split_method == 'by_current_cost_price' and total_cost:
                                per_unit = (line.price_unit / total_cost)
                                value = valuation.former_cost * per_unit
                            else:
                                value = (line.price_unit / total_line)
                            if digits:
                                value = tools.float_round(value, decimal_precision, rounding_method='UP')
                                fnc = min if line.price_unit > 0 else max
                                value = fnc(value, line.price_unit - value_split)
                                value_split += value

                            if valuation.id not in towrite_dict:
                                towrite_dict[valuation.id] = value
                            else:
                                towrite_dict[valuation.id] += value
            self.purchase_id.write({
                'as_cost_id':self.id
                })
        else:
            for cost in self.filtered(lambda cost: cost.picking_id.move_lines):
                total_qty = 0.0
                total_cost = 0.0
                total_weight = 0.0
                total_volume = 0.0
                total_line = 0.0
                all_val_line_values = cost.get_valuation_lines()
                for val_line_values in all_val_line_values:
                    weight= val_line_values['weight']
                    quantity= val_line_values['quantity']
                    former_cost= val_line_values['former_cost']
                    volume= val_line_values['volume']
                    ttweight = val_line_values['tweight']
                    ttquantity = val_line_values['tquantity']
                    ttformer_cost = val_line_values['tformer_cost']
                    ttvolume = val_line_values['tvolume']
                    tweight = 0.00
                    tquantity = 0.00
                    tformer_cost = 0.00
                    tvolume = 0.00
                    val_line_head={}
                    val_line={}
                    total_line += 1
                    for cost_line in cost.cost_lines:
                        price_line = cost_line.price_unit
                        if cost_line.as_facturado==True:
                            price_line= (cost_line.price_unit*87)/100
                        val_line_head = {
                            'cost_id': cost.id, 
                            'cost_line_id': cost_line.id,
                            'product_id': val_line_values['product_id'],
                            'line_id': val_line_values['line_id'],
                            'move_id': val_line_values['move_id'],
                            }
                        if cost_line.split_method == 'by_quantity' and ttquantity > 0.00:
                            val_line = {
                                'quantity': price_line * (quantity/ttquantity),
                                'weight': 0.00,
                                'volume': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                            tquantity += price_line * (quantity/ttquantity)
                        elif cost_line.split_method == 'by_weight' and ttweight > 0.00:
                            val_line = {
                                'weight': price_line * (weight/ttweight),
                                'quantity': 0.00,
                                'volume': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                            tweight+= price_line * (weight/ttweight)
                        elif cost_line.split_method == 'by_volume' and ttvolume > 0.00:
                            val_line = {
                                'volume': price_line * (volume/ttvolume),
                                'quantity': 0.00,
                                'weight': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                            
                            tvolume += price_line * (volume/ttvolume)
                        elif cost_line.split_method == 'by_current_cost_price' and ttformer_cost>0.00:
                            val_line = {
                                'former_cost': price_line * (former_cost/ttformer_cost),
                                'quantity': 0.00,
                                'volume': 0.00,
                                'weight': 0.00,
                                }
                            val_line.update(val_line_head)
                            tformer_cost += price_line * (former_cost/ttformer_cost)
                        elif cost_line.split_method == 'equal':
                            val_line = {
                                'former_cost': (line.price_unit / total_line),
                                'quantity': 0.00,
                                'volume': 0.00,
                                'former_cost': 0.00,
                                }
                            val_line.update(val_line_head)
                        else:
                            raise UserError(_("Por favor revise la configuracion de los productos si es peso y volumen no puden estar en cero"))
                        
                        self.env['stock.valuation.adjustment.lines'].create(val_line)
                    line_order = self.env['purchase.order.line'].sudo().search([('id', '=', val_line_values['line_id'])])
                    sum_todo= tweight+tquantity+tformer_cost+tvolume
                    vals_summary = ({
                        'cost_id': cost.id, 
                        'move_id': val_line_values['move_id'],
                        'line_id': val_line_values['line_id'],
                        'product_id': val_line_values['product_id'],
                        'weight': line_order.product_id.weight,
                        'price_unit': line_order.price_unit,
                        'volume': line_order.product_id.volume,
                        'quantity': line_order.product_qty,
                        'as_value_fob': line_order.price_unit * line_order.product_qty,
                        'as_cost_fob': sum_todo,
                        'as_cost_total': (line_order.price_unit * line_order.product_qty)+sum_todo,
                        'as_cost_unit': sum_todo / line_order.product_qty,
                        'as_cost_new': line_order.price_unit + (sum_todo / line_order.product_qty),
                    })
                    summary= self.env['as.stock.valuation.summary.lines'].sudo().search([('cost_id', '=', cost.id),('line_id', '=', val_line_values['line_id'])])
                    if summary:
                        summary.update(vals_summary)
                    else:
                        self.env['as.stock.valuation.summary.lines'].create(vals_summary)
                    total_qty += val_line_values.get('quantity', 0.0)
                    total_weight += val_line_values.get('weight', 0.0)
                    total_volume += val_line_values.get('volume', 0.0)

                    former_cost = val_line_values.get('former_cost', 0.0)
                    total_cost += tools.float_round(former_cost, precision_digits=digits[1]) if digits else former_cost

                    total_line += 1
                for line in cost.cost_lines:
                    value_split = 0.0
                    for valuation in cost.valuation_adjustment_lines:
                        value = 0.0
                        if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                            if line.split_method == 'by_quantity' and total_qty:
                                per_unit = (line.price_unit / total_qty)
                                value = valuation.quantity * per_unit
                            elif line.split_method == 'by_weight' and total_weight:
                                per_unit = (line.price_unit / total_weight)
                                value = valuation.weight * per_unit
                            elif line.split_method == 'by_volume' and total_volume:
                                per_unit = (line.price_unit / total_volume)
                                value = valuation.volume * per_unit
                            elif line.split_method == 'equal':
                                value = (line.price_unit / total_line)
                            elif line.split_method == 'by_current_cost_price' and total_cost:
                                per_unit = (line.price_unit / total_cost)
                                value = valuation.former_cost * per_unit
                            else:
                                value = (line.price_unit / total_line)
                            if digits:
                                value = tools.float_round(value, precision_digits=digits[1], rounding_method='UP')
                                fnc = min if line.price_unit > 0 else max
                                value = fnc(value, line.price_unit - value_split)
                                value_split += value

                            if valuation.id not in towrite_dict:
                                towrite_dict[valuation.id] = value
                            else:
                                towrite_dict[valuation.id] += value
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True

    # @api.multi
    def button_draft(self):
        if self.account_move_id:
            self.account_move_id.button_cancel()
            self.account_move_id=False
        return self.write({'state': 'draft','account_move_id':False})

    # @api.multi
    def button_draft_simple(self):
        if self.account_move_id:
            self.account_move_id.button_cancel()
            self.account_move_id=False
        return self.write({'state': 'draft'})
        
    # @api.multi
    def button_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        # if not self._check_sum():
        #     raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'move_type': 'entry',
                'line_ids': [],
            }
            total=0.00
            asientod= []
            for line in cost.as_valuation_summary_lines:
                line_quant = self.env['as.valuation.location'].sudo().search([('product_id', '=', line.move_id.product_id.id),('location_id', '=', line.move_id.location_dest_id.id)])
                if line_quant:
                    line_quant.unit_cost = line.as_cost_new
                price_convert = self.company_id.currency_id._convert(line.as_cost_new,line.move_id.purchase_line_id.currency_id, self.company_id, self.date,round=False)
                line.move_id.write({
                    'price_unit': price_convert,
                    'as_price_unit_import': price_convert,
                })
                line.move_id.purchase_line_id.as_price_unit_import = price_convert
                if line.move_id.state =='done':
                    line.move_id.product_price_update_before_done()
                    modsales_margin = self.env['ir.module.module'].sudo().search([("name","=","as_sales_margin"),("state","=","installed")])
                    if modsales_margin:
                        cost.purchase_id.update_fixed_import(line.move_id.product_id,line.as_cost_new,cost.company_id.currency_id)
                else:
                    raise UserError(_('El movimiento de inventario debe estar confirmado para calcular el costo y precio de venta.'))
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                #move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)
                total += line.as_cost_fob
            if cost.account_move_id:
                cost.write({'state': 'done'})
            if not cost.account_move_id:
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                linked_layer = line.move_id.stock_valuation_layer_ids[:1]

                # Prorate the value at what's still in stock
                cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                if not cost.company_id.currency_id.is_zero(cost_to_add):
                    valuation_layer = self.env['stock.valuation.layer'].create({
                        'value': cost_to_add,
                        'unit_cost': 0,
                        'quantity': 0,
                        'remaining_qty': 0,
                        'stock_valuation_layer_id': linked_layer.id,
                        'description': cost.name,
                        'stock_move_id': line.move_id.id,
                        'product_id': line.move_id.product_id.id,
                        'stock_landed_cost_id': cost.id,
                        'company_id': cost.company_id.id,
                    })
                    linked_layer.remaining_value += cost_to_add
                    valuation_layer_ids.append(valuation_layer.id)
                # Update the AVCO
                product = line.move_id.product_id
                if product.cost_method == 'average' and not float_is_zero(product.quantity_svl, precision_rounding=product.uom_id.rounding):
                    product.with_company(self.company_id).sudo().with_context(disable_auto_svl=True).standard_price += cost_to_add / product.quantity_svl
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                account_in = cost.account_journal_id.payment_debit_account_id.id
                account_out = cost.account_journal_id.payment_credit_account_id.id
                move_vals['line_ids']+= cost._create_accounting_entries(move,account_in,account_out,total) 

                move = move.create(move_vals)
                cost.write({'state': 'done', 'account_move_id': move.id})
                move.post()
        return True
        
    def _create_accounting_entries(self, move,account_in,account_out, qty_out):
        debit_account_id = account_in

        already_out_account_id = False
        credit_account_id = account_out

        return self._create_account_move_line(move, credit_account_id, debit_account_id, qty_out, already_out_account_id)
    
    def _create_account_move_line(self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        AccountMoveLine = []

        base_line = {
            'name': self.name,
        }
        debit_line = dict(base_line, account_id=debit_account_id,debit=qty_out,credit=0.00)
        credit_line = dict(base_line, account_id=credit_account_id,debit=0.00,credit=qty_out)
        AccountMoveLine.append([0, 0, debit_line])
        AccountMoveLine.append([0, 0, credit_line])

        return AccountMoveLine


    #toma los valores de las lineas de costo
    def get_valuation_lines(self):
        lines = []
        #usando factores para el calculo de totales
        total_qty = 0.00
        total_weight = 0.00
        total_volume = 0.00
        former_cost= 0.00
        former_cost_fob = 0.00
        if self.as_document_type == 'compra':
            #se totalizan para el calculo del factor
            currency_default= self.env.user.company_id.currency_id
            for val_line_values in self.mapped('purchase_id').mapped('order_line'):
                currency_converter= val_line_values.order_id.currency_id
                price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,val_line_values.price_unit)
                total_qty += val_line_values.product_qty
                total_weight += val_line_values.product_id.weight
                total_volume += val_line_values.product_id.volume
                former_cost += price_unit
                former_cost_fob += price_unit * val_line_values.product_qty

            for line in self.mapped('purchase_id').mapped('order_line'):
                currency_converter= line.order_id.currency_id
                price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line.price_unit)
                move =  self.env['stock.move'].sudo().search([('purchase_line_id', '=', line.id),('state','!=','cancel')])
                
                vals = {
                    'product_id': line.product_id.id,
                    'line_id': line.id,
                    'move_id': move.id,
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

            if not lines and self.mapped('purchase_id'):
                raise UserError(_("No puede aplicar costos de aterrizaje en las transferencias elegidas. Los costos de aterrizaje solo se pueden aplicar para productos con valuación de inventario automatizada"))
        else:
             #se totalizan para el calculo del factor
            for val_line_values in self.mapped('picking_id').mapped('move_lines'):
                total_qty += val_line_values.product_qty
                total_weight += val_line_values.product_id.weight
                total_volume += val_line_values.product_id.volume
                former_cost += val_line_values.price_unit

            for line in self.mapped('picking_id').mapped('move_lines'):                
                vals = {
                    'product_id': line.product_id.id,
                    'line_id': line.purchase_line_id.id,
                    'move_id': line.id,
                    'quantity': (line.product_qty),
                    'tquantity': (total_qty),
                    'former_cost': (line.price_unit),
                    'tformer_cost': (former_cost),
                    'weight': (line.product_id.weight),
                    'tweight': (total_weight),
                    'volume': (line.product_id.volume),
                    'tvolume': (total_volume),
                }
                lines.append(vals)

            if not lines and self.mapped('picking_id'):
                raise UserError(_("No puede aplicar costos de aterrizaje en las transferencias elegidas. Los costos de aterrizaje solo se pueden aplicar para productos con valuación de inventario automatizada"))
        return lines

    # @api.multi
    def recalcular_costo(self,move_id,precio):
        line_move = self.env['stock.move'].sudo().search([('id', '=', move_id)])
        line_move.write({
                'price_unit': precio,
        })

    # @api.multi
    def convert_amount_line_bruto(self,currency_default,currency_converter,amount):
        if currency_default != currency_converter:
            digits = dp.get_precision('Product Price')
            return currency_converter._convert(amount,currency_default, self.company_id, self.date,round=False)
        else:
            return amount

class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    _description = 'As Valuation Adjustment Lines'

    line_id = fields.Many2one('purchase.order.line', 'Linea de Compra', readonly=True)

class AdjustmentResumenLines(models.Model):
    _name = 'as.stock.valuation.summary.lines'
    _description = 'Valuation Adjustment Lines summary'
    #modelo que permite resumir las cantidades
    cost_id = fields.Many2one(
        'stock.landed.cost', 'Landed Cost',
        ondelete='cascade', required=True,index=True)
    move_id = fields.Many2one('stock.move', 'Stock Move', readonly=True)
    line_id = fields.Many2one('purchase.order.line', 'Linea de Compra', readonly=True, index=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float(
        'Quantity',
        digits=0, required=True)
    weight = fields.Float(
        'Weight',
        digits=dp.get_precision('Stock Weight'))
    volume = fields.Float('Volume')
    additional_landed_cost = fields.Float('costo adicional')
    price_unit = fields.Float('Precio Unitario',digits=dp.get_precision('Product Price'))
    as_value_fob = fields.Float('Valor FOB',digits=dp.get_precision('Product Price'))
    as_cost_fob = fields.Float('Costo Total',digits=dp.get_precision('Product Price'))
    as_cost_total = fields.Float('Costo Total',digits=dp.get_precision('Product Price'))
    as_cost_unit = fields.Float('Costo Unitario',digits=dp.get_precision('Product Price'))
    as_cost_new = fields.Float('Nuevo Costo',digits=dp.get_precision('Product Price'))

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'
    # invoice_ids campo que relaciona las facturas con

    as_supplier_costo = fields.Many2one('res.partner', 'Proveedor', help=u'Proveedor del costo de importacion.')
    as_journal_id = fields.Many2one('account.journal', 'Diario')
    as_scan_qr = fields.Char(string="QR factura", help="Click aqui para que el cursor lea el codigo de QR de la factura de compra")
    as_nit = fields.Char(string="NIT")
    as_razon_social = fields.Char(string="Razon Social")
    as_tipo_factura  = fields.Many2one('as.tipo.factura','Tipo de Factura', help=u'Tipo de factura para el registro de libro de compra y calculo del monto exento automatico.')
    as_fecha_factura = fields.Date(string="Fecha gasto")
    as_numero_factura = fields.Char(string='No Factura', help='Numero de factura.')
    as_codigo_control = fields.Char('Codigo Control', size=50)
    as_numero_autorizacion = fields.Char(string='No Autorizacion', help='Numero de Autorizacion.', size=80, digits=(80, 0))
    as_monto_excento = fields.Float(string="Monto Excento")
    as_numero_dui  = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.')
    as_numero_autorizacion_dui = fields.Char(string='No Autorizacion Dui', help='Numero de Autorizacion.', size=80, digits=(80, 0))
    as_invoice_id = fields.Many2one('account.move', string="Factura", copy=False)
    as_facturado = fields.Boolean(string="Facturado", default=False)
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion')
    as_tipo_documento  = fields.Selection([('Factura','Factura'),('Prefactura/Recibo','Prefactura/Recibo')] ,'Tipo de documento', help=u'Tipo de documento que pertenece la factura.', default='Factura')
    as_importe_ic = fields.Float(string='Importe ICE ', default=0.0)
    as_importe_iehd = fields.Float(string='Importe IEHD ', default=0.0)
    as_importe_ipj = fields.Float(string='Importe IPJ ', default=0.0)
    as_tasas = fields.Float(string='Tasas ', default=0.0)
    as_exentos = fields.Float(string='Importes exentos', default=0.0)
    as_gift_card = fields.Float(string='Importes Gift Card', default=0.0)
    as_compras_gravadas = fields.Float(string='Importe compras gravadas a tasa cero', default=0.0)

    as_codigo_control_compra = fields.Char('Codigo Control')
    as_numero_autorizacion_compra  = fields.Char(string='No Autorizacion', help='Numero de Autorizacion.', digits=(15, 0))
    as_impuesto_especifico = fields.Float(string='Otro no sujeto a credito fiscal', default=0.0)
    as_tipo_compra = fields.Many2one('as.tipo.compra',string='Tipo de compra')
    as_scan_qr = fields.Char(string="QR factura", help="Click aqui para que el cursor lea el codigo de QR de la factura de compra")
    as_payment_teas_id = fields.Many2one('account.payment.term', string="Plazo de pago")
    # as_costo_cero = fields.Boolean(string='Tasa en Cero', default=False)   
    # as_iva = fields.Boolean(string='IVA', default=False)   

    @api.onchange('as_tipo_factura')
    def onchange_as_tipo_factura(self):  
        if self.as_tipo_factura.as_calcular: 
            self.as_monto_excento =  (self.price_unit*(self.as_tipo_factura.as_factor/100))
        
    @api.onchange('as_fecha_factura')
    def onchange_date(self):
        for inv in self:
            if inv.as_invoice_id:
                inv.as_invoice_id.write({'date_invoice':inv.as_fecha_factura})

    #cargar el nit y la razon social del proveedor
    @api.onchange('as_supplier_costo')
    def onchange_supplier(self):
        for inv in self:
            inv.as_nit = inv.as_supplier_costo.vat
            inv.as_razon_social = inv.as_supplier_costo.as_razon_social

    #formulario de edicion para factura 
    # @api.multi
    def action_edit_form(self):
        action = self.env.ref('as_bo_purchase_import.action_open_window_edit')
        result = action.read()[0]
        result['target'] = 'new'
        result['flags'] = {'form': {'action_buttons': True}}
        result['res_id'] = self.id
        return result
    

    """ Funcion de escanear qr """
    @api.onchange('as_scan_qr')
    def escanear_codigo_qr(self):
        if self.as_scan_qr:
            array = (self.as_scan_qr).split(']')
            if len(array) != 12:
                raise UserError(_("Formato de QR invalido"))
            self.as_nit = array[0]
            self.as_numero_factura = str(int(array[1]))
            self.as_numero_autorizacion = array[2]
            fecha = array[3].split("-")
            self.as_fecha_factura = fecha[2] +"-"+ fecha[1] + "-" + fecha[0]
            self.as_codigo_control = array[6]
            self.as_codigo_control = self.as_codigo_control.replace("'",'-')
            # self.as_tasas = array[8]  PARA CUANDO EXISTAN LOS CAMPOS
            # self.as_compras_gravadas = array[9]
            self.as_scan_qr = None

    #crear factura de importacion
    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        for order in self:
            order = order.with_company(order.env.user.company_id)
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
          
            if not float_is_zero(order.price_unit, precision_digits=precision):
                invoice_vals['invoice_line_ids'].append((0, 0, order._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
            # factura_obj.action_invoice_open()
        self.as_invoice_id = moves.id
        self.cost_id._verifica_calculo()
        return moves

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        # journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        journal = self.as_journal_id
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        if self.as_nit == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese nit') )
        if self.as_razon_social == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese razon social') )
        if self.as_codigo_control == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese codigo de control') )
        if self.as_tipo_factura == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese tipo de factura') )
        if self.as_numero_autorizacion == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese numero de autorizacion') )
        if self.as_numero_factura == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese numero de factura') )
        if self.as_facturado == True:
            tipo_factura='Factura'
        else:
            tipo_factura='Prefactura/Recibo'
        invoice_vals = {
            'move_type': move_type,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.cost_id.name,
            'invoice_line_ids': [],
            'company_id': self.env.user.company_id.id,
            'partner_id': self.as_supplier_costo.id,
            'date_invoice' : self.as_fecha_factura,
            'as_tipo_documento' : tipo_factura,
            'as_nit' : self.as_nit,
            'as_razon_social' : self.as_razon_social,
            'as_numero_factura_compra' : self.as_numero_factura,
            'as_codigo_control_compra' : self.as_codigo_control,
            'as_numero_autorizacion_compra' : self.as_numero_autorizacion,
            'as_tipo_factura' : self.as_tipo_factura.id,
            'as_impuesto_especifico' : self.as_monto_excento,
            'as_tipo_retencion' : self.as_tipo_retencion.id,
            'invoice_origin' : self.cost_id.name,
        }
        return invoice_vals

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        taxes=[]
        price_unit = 0.0
        if self.as_facturado == True:
            tipo_factura='Factura'
            if self.as_tipo_factura.as_iva != True and self.as_tipo_factura.as_costo_cero != True:
                for tax in self.product_id.supplier_taxes_id:
                    taxes.append(tax.id)
        else:
            tipo_factura='Prefactura/Recibo'
        if self.as_tipo_factura.as_iva == False:
            price_unit = self.price_unit
        else:
            price_unit =  self.price_unit       
        res = {
            'name': '%s: %s' % (self.cost_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'quantity': 1,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, taxes)],
        }
      
        res.update({
            # 'move_id': move.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'partner_id': self.as_supplier_costo.id,
        })
        return res

    # def action_create_invoice(self):
    #     taxes=[]
    #     price_unit = 0.0
    #     for datos in self:
    #         if datos.as_facturado == True:
    #             tipo_factura='Factura'
    #             if datos.as_tipo_factura.as_iva != True and datos.as_tipo_factura.as_costo_cero != True:
    #                 for tax in datos.product_id.supplier_taxes_id:
    #                     taxes.append(tax.id)
    #         else:
    #             tipo_factura='Prefactura/Recibo'
    #         if datos.as_tipo_factura.as_iva == False:
    #             price_unit = datos.price_unit
    #         else:
    #             price_unit =  datos.price_unit             
    #         values = {
    #             'partner_id': datos.as_supplier_costo.id,
    #             #'account_id' : datos.as_supplier_costo.property_account_payable_id.id,
    #             'date_invoice' : datos.as_fecha_factura,
    #             'as_tipo_documento' : tipo_factura,
    #             'as_nit' : datos.as_nit,
    #             'as_razon_social' : datos.as_razon_social,
    #             'as_numero_factura_compra' : datos.as_numero_factura,
    #             # 'invoice_number' : datos.as_numero_factura,
    #             'as_codigo_control_compra' : datos.as_codigo_control,
    #             'as_numero_autorizacion_compra' : datos.as_numero_autorizacion,
    #             'as_tipo_factura' : datos.as_tipo_factura.id,
    #             'as_impuesto_especifico' : datos.as_monto_excento,
    #             # 'as_tipo_retencion' : datos.as_tipo_retencion.id,
    #             # 'as_costo_cero' : datos.as_costo_cero,
    #             # 'as_iva' : datos.as_iva,
    #             'as_numero_dui' :datos.as_numero_dui,
    #             'reference' : '',
    #             # 'debit': 0.00,
    #             # 'credit': 0.00,
    #             'state' : 'draft',
    #             # 'origin' : datos.cost_id.purchase_id.name,
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': datos.name,
    #                 'price_unit': price_unit,
    #                 'quantity':1,
    #                 'product_id':datos.product_id.id,
    #                 'account_id' : datos.as_supplier_costo.property_account_payable_id.id})],}

    #         factura_obj = self.env['account.move'].with_context(
    #             default_move_type='in_invoice',state='draft').create(values)
    #         factura_obj.write({
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': datos.name,
    #                 'price_unit': price_unit,
    #                 'quantity':1,
    #                 'product_id':datos.product_id.id,
    #                 'account_id' : datos.as_supplier_costo.property_account_payable_id.id})],
    #         })
            
    #         # factura_obj.update({
    #         #     'residual':factura_obj.amount_total,
    #         #     'residual_signed':factura_obj.amount_total,
    #         # })
    #         # factura_obj.action_invoice_open()
    #         datos.as_invoice_id = factura_obj.id
    #     self.cost_id._verifica_calculo()
    #     return factura_obj