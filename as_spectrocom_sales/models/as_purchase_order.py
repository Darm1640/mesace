from odoo import models, fields, api,_,SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class Purchase_order(models.Model):
    _inherit = 'purchase.order'

    as_descuento_global = fields.Float(string="Descuento global")
    as_sale_id = fields.Many2one('sale.order', string="Venta")

    as_aprovador = fields.Char(string="Usuario que aprobo")
    as_aprovador_empleado = fields.Integer(string="Usuario que aprobo")
    as_diario_purchase = fields.Many2one('account.journal', string= "Diario para factura",domain=[("type", "=", "purchase")])

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    if self.as_tipo_retencion.id:
                        picking.as_tipo_retencion = self.as_tipo_retencion.id
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True
    
    def _prepare_invoice(self):
        res = super(Purchase_order, self)._prepare_invoice()
        if self.as_diario_purchase:
            res['journal_id']= self.as_diario_purchase.id
        else:
            raise UserError(_("No se ha seleccionado ningun valor para el campo 'Diario para factura'"))
        return res
    
    def button_approve(self, force=False):
        res = super(Purchase_order, self).button_approve(force=force)
        self.as_aprovador = str(self.env.user.partner_id.name)
        self.as_aprovador_empleado = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        return res

class Purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    as_descuento_linea = fields.Float(string="Descuento monto")
    as_activo = fields.Char(string="Id activo")
    as_type_total = fields.Float(string="Total")
    price_unit = fields.Float(string="Total", digits=(8,10))
    
    @api.onchange("as_type_total","product_qty")
    def lineas_descuentos_total(self):
        for discount in self:
            if discount.as_type_total != 0:
                discount.price_unit = float("{0:.3f}".format(discount.as_type_total)) / float("{0:.3f}".format(discount.product_qty))      
    
    @api.onchange("product_id","price_unit")
    def lineas_descuentos(self):
        for discount in self:
            discount.as_descuento_linea = discount.order_id.as_descuento_global
            discount.price_subtotal = discount.price_subtotal - discount.as_descuento_linea

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded']-line.as_descuento_linea,
            })

    @api.model
    def _prepare_account_move_line(self, move=False):
        res = super(Purchase_order_line, self)._prepare_account_move_line(move=False)
        if self.order_id.as_project_id.analytic_account_id.id != False:
            res['analytic_account_id'] = self.order_id.as_project_id.analytic_account_id.id
        else:
            res['analytic_account_id'] = self.account_analytic_id.id
        cont = 0
        cont += 1
        return res