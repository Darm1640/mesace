from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
#Generacion del QR
import qrcode

from odoo import api, fields, models, tools, _
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class AsLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    _description = 'As Stock Landed Cost'

    # @api.multi
    def _purchase_available(self):
        purchase_with_cost= self.env['purchase.order'].sudo().search([('state', '=', 'purchase'),('as_importacion', '=', True)])
        ids_not=[]
        for purchase in purchase_with_cost:
            if not purchase.as_cost_id:
                ids_not.append(purchase.id)
        return [('id', 'in', tuple(ids_not))]

    # @api.multi
    def _purchase_presupuesto(self):
        purchase_with_cost= self.env['purchase.order'].sudo().search([('state', '=', 'purchase'),('as_importacion', '=', True)])
        ids_not=[]
        for purchase in purchase_with_cost:
            if not purchase.as_cost_id:
                ids_not.append(purchase.id)
        return [('id', 'in', tuple(ids_not))]

    purchase_ids = fields.Many2many('purchase.order', 'as_landed_uno',string='Pedido de Compra', copy=False, states={'done': [('readonly', True)]})
    purchase_est_ids = fields.Many2many('purchase.order','as_landed_dos', string='Presupuesto de Compra', copy=False, states={'done': [('readonly', True)]})
    as_document_type = fields.Selection(selection_add=[('multi', 'Multiples Compras'),('estimado', 'Estimado de Compras')])

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
                'as_cost_price': lines.price_unit_est,
                'split_method': lines.split_method,
                'account_id': lines.account_id.id,
                # 'template_cost_id': self.purchase_template_id.id,
            }
            line_cost.append((0, 0, data))
        self.cost_lines = line_cost

    #funcion heredada que calcula los montos d elas solapas
    @api.model
    def create(self, vals):
        res = super(AsLandedCost, self).create(vals)
        for purchase in res.purchase_ids:
            purchase.write({
                'as_cost_id':res.id
            })
        if res.as_document_type=='estimado':
            for purchase in res.purchase_est_ids:
                purchase.write({
                    'as_cost_id':False
                })
        return res

    # @api.multi
    def write(self, vals):
        res = super(AsLandedCost, self).write(vals)
        for purchase in self.purchase_ids:
            purchase.write({
                'as_cost_id':self.id
            })
        if self.as_document_type=='estimado':
            for purchase in self.purchase_est_ids:
                purchase.write({
                    'as_cost_id':False
                })
        return res

    @api.onchange('purchase_ids')
    def onchange_amount_purchases(self):
        monto = 0.0
        currency_default = self.env.user.company_id.currency_id
        for purchase in self.purchase_ids:
            currency_purchase = purchase.currency_id
            monto_compra = currency_default._compute(currency_purchase,currency_default,purchase.amount_total)
            monto+=monto_compra
        self.amount_total_purchase+= monto

    # @api.one
    @api.depends('cost_lines.price_unit','purchase_id','cost_lines.as_cost_price')
    def _compute_total_amount(self):
        if self.as_document_type=='estimado':
            self.amount_total = sum(line.as_cost_price for line in self.cost_lines)
            self.amount_total_gasto = self.amount_total_purchase + self.amount_total
        else:
            self.amount_total = sum(line.price_unit for line in self.cost_lines)
            self.amount_total_gasto = self.amount_total_purchase + self.amount_total

    @api.onchange('purchase_est_ids')
    def onchange_amount_purchasesp(self):
        monto = 0.0
        currency_default = self.env.user.company_id.currency_id
        for purchase in self.purchase_est_ids:
            currency_purchase = purchase.currency_id
            monto_compra = currency_default._compute(currency_purchase,currency_default,purchase.amount_total)
            monto+=monto_compra
        self.amount_total_purchase+= monto

                    
    # @api.multi
    def compute_landed_cost_prespupuesto(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()
        digits = dp.get_precision('Product Price')
        towrite_dict = {}
        currency_default= self.env.user.company_id.currency_id    
        if self.as_document_type=='estimado':
            lines_orders = self.env['purchase.order.line']
            for purchase in self.purchase_est_ids:
                lines_orders+=purchase.order_line
            for cost in self:
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
                        price_line = cost_line.as_cost_price
                        if cost_line.as_facturado==True and cost_line.as_tipo_factura.as_costo_cero != True:
                            price_line= (cost_line.as_cost_price*87)/100
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
                    sum_todo= (tweight+tquantity+tformer_cost+tvolume)
                    currency_default= self.env.user.company_id.currency_id
                    currency_converter= line_order.order_id.currency_id
                    price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line_order.price_unit)
                    vals_summary = ({
                        'cost_id': cost.id, 
                        'move_id': val_line_values['move_id'],
                        'line_id': val_line_values['line_id'],
                        'product_id': val_line_values['product_id'],
                        'weight': line_order.product_id.weight,
                        'as_qty': line_order.qty_received,
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
                    total_cost += tools.float_round(former_cost, precision_digits=1) if digits else former_cost

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
                                value = tools.float_round(value, precision_digits=1, rounding_method='UP')
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
                    sum_todo= (tweight+tquantity+tformer_cost+tvolume)
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
                    total_cost += tools.float_round(former_cost, precision_digits=1) if digits else former_cost

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
                                value = tools.float_round(value, precision_digits=1, rounding_method='UP')
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
        elif self.as_document_type=='multi':
            lines_orders = self.env['purchase.order.line']
            for purchase in self.purchase_ids:
                lines_orders+=purchase.order_line
            for cost in self:
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
                    sum_todo= (tweight+tquantity+tformer_cost+tvolume)
                    currency_default= self.env.user.company_id.currency_id
                    currency_converter= line_order.order_id.currency_id
                    price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line_order.price_unit)
                    vals_summary = ({
                        'cost_id': cost.id, 
                        'move_id': val_line_values['move_id'],
                        'line_id': val_line_values['line_id'],
                        'product_id': val_line_values['product_id'],
                        'weight': line_order.product_id.weight,
                        'as_qty': line_order.qty_received,
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
                    total_cost += tools.float_round(former_cost, precision_digits=1) if digits else former_cost

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
                                value = tools.float_round(value, precision_digits=1, rounding_method='UP')
                                fnc = min if line.price_unit > 0 else max
                                value = fnc(value, line.price_unit - value_split)
                                value_split += value

                            if valuation.id not in towrite_dict:
                                towrite_dict[valuation.id] = value
                            else:
                                towrite_dict[valuation.id] += value
            # self.purchase_id.write({
            #     'as_cost_id':self.id
            #     })
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
                    total_cost += tools.float_round(former_cost, precision_digits=1) if digits else former_cost

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
                                value = tools.float_round(value, precision_digits=1, rounding_method='UP')
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
                move = self.env['stock.move'].sudo().search([('purchase_line_id', '=', line.id),('state','!=','cancel')])
                
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
        elif self.as_document_type == 'multi':
            #se totalizan para el calculo del factor
            currency_default= self.env.user.company_id.currency_id
            for val_line_values in self.mapped('purchase_ids').mapped('order_line'):
                currency_converter= val_line_values.order_id.currency_id
                price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,val_line_values.price_unit)
                total_qty += val_line_values.product_qty
                total_weight += val_line_values.product_id.weight
                total_volume += val_line_values.product_id.volume
                former_cost += price_unit
                former_cost_fob += price_unit * val_line_values.product_qty

            for line in self.mapped('purchase_ids').mapped('order_line'):
                currency_converter= line.order_id.currency_id
                price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line.price_unit)
                move = self.env['stock.move'].sudo().search([('purchase_line_id', '=', line.id)],limit=1)
                
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

            if not lines and self.mapped('purchase_ids'):
                raise UserError(_("No puede aplicar costos de aterrizaje en las transferencias elegidas. Los costos de aterrizaje solo se pueden aplicar para productos con valuación de inventario automatizada"))
        elif self.as_document_type == 'estimado':
            #se totalizan para el calculo del factor
            currency_default= self.env.user.company_id.currency_id
            for val_line_values in self.mapped('purchase_est_ids').mapped('order_line'):
                currency_converter= val_line_values.order_id.currency_id
                price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,val_line_values.price_unit)
                total_qty += val_line_values.product_qty
                total_weight += val_line_values.product_id.weight
                total_volume += val_line_values.product_id.volume
                former_cost += price_unit
                former_cost_fob += price_unit * val_line_values.product_qty

            for line in self.mapped('purchase_est_ids').mapped('order_line'):
                currency_converter= line.order_id.currency_id
                price_unit= self.convert_amount_line_bruto(currency_default,currency_converter,line.price_unit)
                move = self.env['stock.move'].sudo().search([('purchase_line_id', '=', line.id)],limit=1)
                
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

            if not lines and self.mapped('purchase_est_ids'):
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
    def button_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        if self.as_document_type == 'estimado':
            raise UserError(_('No se pueden Validar compras en Borrador, cambie el tipo y seleccione compra.'))
        # if not self._check_sum():
        #     raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
            }
            total=0.00
            asientod= []
            for line in cost.as_valuation_summary_lines.filtered(lambda line: line.move_id):
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
                        if cost.as_document_type == 'multi':
                            for purchase in cost.purchase_ids:
                                purchase.update_fixed_import(line.move_id.product_id,line.as_cost_new,cost.company_id.currency_id)
                        elif cost.as_document_type == 'compra':
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
                for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                    cost_to_add = (line.move_id.stock_valuation_layer_ids.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost

                    new_landed_cost_value = line.move_id.stock_valuation_layer_ids.value + line.additional_landed_cost
                    line.move_id.stock_valuation_layer_ids.write({
                        # 'landed_cost_value': new_landed_cost_value,
                        'value': line.move_id.stock_valuation_layer_ids.value + line.additional_landed_cost,
                        'remaining_value': line.move_id.stock_valuation_layer_ids.remaining_value + cost_to_add,
                    })              
                    # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                    # in stock.
                account_in = cost.account_journal_id.payment_debit_account_id.id
                account_out = cost.account_journal_id.payment_credit_account_id.id
                move_vals['line_ids']+= cost._create_accounting_entries(move,account_in,account_out,total) 
                line_move = self.env['account.move.line']
                move = move.create(move_vals)
                for cost_line in cost.cost_lines:
                    for line_invoice in cost_line.as_invoice_id.line_ids:
                        line_move |= line_invoice.with_context(move_id = move.id,check_move_validity=False).copy({
                            'move_id': move.id,
                        }) 
                cost.write({'state': 'done', 'account_move_id': move.id})
                move.post()
        return True