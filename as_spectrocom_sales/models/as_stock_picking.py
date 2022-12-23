from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"
    as_lote = fields.Char("Lote/Nº de serie")
    as_check_devolucion = fields.Boolean(string="Producto por devolver", default=True)
    
class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking" 

    location_id = fields.Many2one('stock.location', ' Ubicación de devolución',domain="")
    as_selector = fields.Boolean(string="Seleccionar todo", default=True)

    @api.onchange('as_selector')
    def as_get_selector1(self):
        for emp in self:
            for line in emp.product_return_moves:
                line.as_check_devolucion = emp.as_selector

    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        new_picking = self.picking_id.copy({
            'move_lines': [],
            'move_line_ids_without_package': False,
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s", self.picking_id.name),
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        for line in new_picking.move_line_ids_without_package:
            line.state = 'draft'
        new_picking.move_line_ids_without_package.unlink()
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                # ======> PARA CATITA!!!! LINEA AGREGADA PARA QUE SE CREEN LOS MOVES QUE TIENEN EL CHECK
                if return_line.as_check_devolucion == True:
                # ======> FIN
                
                    vals = self._prepare_move_default_values(return_line, new_picking)
                    r = return_line.move_id.copy(vals)
                    vals = {}

                    # +--------------------------------------------------------------------------------------------------------+
                    # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                    # |              | returned_move_ids              ↑                                  | returned_move_ids
                    # |              ↓                                | return_line.move_id              ↓
                    # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                    # +--------------------------------------------------------------------------------------------------------+
                    move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                    # link to original move
                    move_orig_to_link |= return_line.move_id
                    # link to siblings of original move, if any
                    move_orig_to_link |= return_line.move_id\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                    move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                    # link to children of originally returned moves, if any. Note that the use of
                    # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                    # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                    # return directly to the destination moves of its parents. However, the return of
                    # the return will be linked to the destination moves.
                    move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids')\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                    vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                    vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                    r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking.id, picking_type_id

    # Funcion heredada para agregar numero de serie en la vista de devolucion de movimientos
    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        quantity = stock_move.product_qty
        for move in stock_move.move_dest_ids:
            if move.origin_returned_move_id and move.origin_returned_move_id != stock_move:
                continue
            if move.state in ('partially_available', 'assigned'):
                quantity -= sum(move.move_line_ids.mapped('product_qty'))
            elif move.state in ('done'):
                quantity -= move.product_qty
        quantity = float_round(quantity, precision_rounding=stock_move.product_uom.rounding)
        lotesito = ''
        for i in stock_move.lot_ids:
            lotesito += i.name + ' '
        return {
            'product_id': stock_move.product_id.id,
            'quantity': quantity,
            'move_id': stock_move.id,
            'uom_id': stock_move.product_id.uom_id.id,
            'as_lote':lotesito
        }
class Stock_picking(models.Model):
    _inherit = 'stock.picking'

    lot_id = fields.Many2one('stock.production.lot', 'Lote', related='as_move_lines.lot_id', readonly=True)
    as_move_lines = fields.One2many('stock.move.line', 'picking_id', string="Stock Moves Lines", copy=True)
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion')

    color = fields.Many2one('stock.location', string= "Custodio")
    as_activo_100_pick = fields.Boolean(string="Invisible aux", compute='_compute_activo',default=False)

    def _compute_activo(self):
        for conf in self:
            conf.as_activo_100_pick = bool(conf.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_activo_100'))
 
    def action_create_assets_2(self):
        self.as_activo_100_pick = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_activo_100'))
        for inv in self:
            moves = self.env['stock.move.line'].search([('picking_id','=',self.id),('as_aux_activo','=','0')], limit=100)
            if len(moves) == 0:
                raise UserError(_('Ya no existen mas activos para crear.'))
            for mv_line in moves:
                if mv_line.as_asset_category_id:
                    mv_line.as_aux_activo = 1
                    mv_line.asset_create()
        return True

    def action_update_activos(self):
        for pick in self:
            #productos sin seguimiento
            for move_line in pick.move_line_ids_without_package:
                # move_line.move_id.lot_ids.name = move_line.move_id.purchase_line_id.as_activo
                if move_line.product_id.tracking == 'none':
                    move_line.qty_done = move_line.product_uom_qty
                    mensaje = '<b style="color:blue">Producto: '+str(move_line.product_id.name)+'cantidad: '+str(move_line.qty_done)+'</b>'
                    self.message_post(body = str(mensaje), content_subtype='html')  
            # productos con seguimiento por serie
            move_lines_commands = []
            if pick.picking_type_id.use_create_lots and not pick.picking_type_id.use_existing_lots:
                for move in pick.move_ids_without_package:
                    prefijo = move_line.move_id.purchase_line_id.as_numero_serie
                    count = 1
                    if move.product_id.tracking == 'serial':
                        if move.move_line_ids:
                            for line_move in move.move_line_ids:
                                lot_name = self.as_get_lot_name(move)
                                line_move.lot_name = lot_name
                                line_move.qty_done = 1
                                count += 1
                        else:
                            for i in range(1,move.product_uom_qty):
                                lot_name = self.as_get_lot_name(move)
                                move_lines_commands.append((0, 0, {
                                    'lot_name': lot_name,
                                    'qty_done': 1,
                                    'product_id': move.product_id.id,
                                    'product_uom_id': move.product_id.uom_id.id,
                                    'location_id': move.location_id.id,
                                    'location_dest_id': move.location_dest_id.id,
                                    'picking_id': move.picking_id.id,
                                }))
                                count += 1
                            move.write({'move_line_ids': move_lines_commands})

    def as_get_lot_name(self,move):
        lot_name = move.purchase_line_id.as_numero_serie
        # lot_name = str(prefijo)+str(product_id.id)+'-'+str(cont)
        return lot_name


class Stock_picking(models.Model):
    _inherit = 'stock.picking.type'

    def get_action_picking_tree_draft(self):
        return self._get_action('as_spectrocom_sales.action_picking_tree_draft')


class as_stock_move(models.Model):
    _inherit = "stock.move.line"
    _description = "lineas de movimiento de inventario"

    as_aux_activo = fields.Integer(string="Campo auxiliar", default = 0)

    @api.onchange('product_id','lot_id','product_uom_qty')
    @api.depends('product_id','lot_id','product_uom_qty')
    def _domain_lote(self):
        lotesd =[]
        lotes_i =[]
        if self.product_id and self.company_id:
            self.env.cr.execute(
                """select spl.id from stock_production_lot spl 
                    join stock_quant sq on sq.lot_id = spl.id
                    where 
                    spl.product_id="""+str(self.product_id.id)+""" and 
                    spl.company_id="""+str(self.company_id.id)+""" and 
                    sq.quantity > 0 and 
                    sq.location_id = """+str(self.location_id.id)+"""
                    group by spl.id"""
            )
            lotes=self.env.cr.fetchall()
            for line in lotes:
                lotes_i.append(line[0])
            return {'domain':{'lot_id': [('id','in', tuple(lotes_i))]}}
        return lotes_i

    def asset_create(self):
        if self.as_asset_category_id:
            # if not self.as_asset_category_id.as_sequence_id:
            #     raise UserError(_('La categoria del Activo debe tener una secuencia seleccionada.'))
            if self.as_asset_category_id.as_sequence_id:
                codigo =  self.as_asset_category_id.as_sequence_id.next_by_id()
            else:
                codigo =  self.move_id.purchase_line_id.as_activo
            vals = {
                'name': self.product_id.display_name,
                'product_id': self.product_id.id,
                'code': codigo or False,
                'category_id': self.as_asset_category_id.id,
                'value': (self.move_id.price_unit*self.move_id.product_uom_qty),
                'partner_id': self.picking_id.partner_id.id,
                'company_id': self.picking_id.company_id.id,
                'currency_id': self.picking_id.company_id.currency_id.id,
                'date': self.picking_id.date_done,
                'as_picking_id': self.picking_id.id,
                'as_move_id': self.id,
                'as_code_assets': codigo,
                'as_lot_id': self.lot_id.id,
                'first_depreciation_manual_date': self.picking_id.date_done,
            }
            changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['account.asset.asset'].create(vals)
            self.picking_id.as_generate_assets = True
            if self.as_asset_category_id.open_asset:
                asset.validate()
        return True

class as_stock_move(models.Model):
    _inherit = "stock.quant"

    @api.constrains('quantity')
    def check_quantity(self):
        for quant in self:
            if float_compare(quant.quantity, 1, precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
                pass
            
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = sum(quants.filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=rounding) > 0).mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
        #     if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
        #         raise UserError(_('It is not possible to reserve more products of %s than you have in stock.', product_id.display_name))
        # elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
        #     # if we want to unreserve
        #     available_quantity = sum(quants.mapped('reserved_quantity'))
        #     if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
        #         raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.', product_id.display_name))
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
                break
        return reserved_quants

class as_StockMove(models.Model):
    _inherit = "stock.move"

    # def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
    #     self.ensure_one()
    #     cost = abs(cost)
    #     account_line_obj = self.env['account.move.line']
    #     if not self.picking_id.as_account_move:
    #         AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
    #         move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
    #         nueva_fun =  self.funcion_aux(qty, cost, credit_account_id, debit_account_id, description)
    #         if self.picking_id.as_tipo_retencion.name == 'Retencion por bienes':
    #             if self.picking_id and self.picking_id.date:
    #                 date = self.picking_id.date.strftime('%Y-%m-%d')
    #             else:
    #                 date = self._context.get('force_period_date', fields.Date.context_today(self))
    #             new_account_move = AccountMove.sudo().create({
    #                 'journal_id': journal_id,
    #                 'line_ids': nueva_fun,
    #                 'date': date,
    #                 'ref': description,
    #                 'stock_move_id': self.id,
    #                 'stock_valuation_layer_ids': [(6, None, [svl_id])],
    #                 'move_type': 'entry',
    #             })
    #             self.picking_id.as_account_move = new_account_move
    #         else:
    #             if move_lines:
    #                 if self.picking_id and self.picking_id.date:
    #                     date = self.picking_id.date.strftime('%Y-%m-%d')
    #                 else:
    #                     date = self._context.get('force_period_date', fields.Date.context_today(self))
    #                 new_account_move = AccountMove.sudo().create({
    #                     'journal_id': journal_id,
    #                     'line_ids': move_lines,
    #                     'date': date,
    #                     'ref': description,
    #                     'stock_move_id': self.id,
    #                     'stock_valuation_layer_ids': [(6, None, [svl_id])],
    #                     'move_type': 'entry',
    #                 })
    #                 self.picking_id.as_account_move = new_account_move
    #                 # new_account_move._post()
    #     else:
    #         AccountMove = self.picking_id.as_account_move.with_context(default_journal_id=journal_id)
    #         move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
    #         for line in move_lines:
    #             line[2]['move_id'] = self.picking_id.as_account_move.id
    #             account_line_obj.with_context(check_move_validity=False,move_id=self.picking_id.as_account_move.id).create(line[2])

    # def funcion_aux(self, qty, cost, credit_account_id, debit_account_id, description):
    #     """
    #     Generate the account.move.line values to post to track the stock valuation difference due to the
    #     processing of the given quant.
    #     """
    #     self.ensure_one()

    #     # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
    #     # the company currency... so we need to use round() before creating the accounting entries.
    #     debit_value = self.company_id.currency_id.round(cost)
    #     credit_value = debit_value

    #     valuation_partner_id = self._get_partner_id_for_valuation_lines()
    #     res = [(0, 0, line_vals) for line_vals in self.funcion_aux_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]

    #     return res

    # def funcion_aux_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
    #     # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
    #     self.ensure_one()
    #     debit_line_vals = {
    #         'name': description,
    #         'product_id': self.product_id.id,
    #         'quantity': qty,
    #         'product_uom_id': self.product_id.uom_id.id,
    #         'ref': description,
    #         'partner_id': partner_id,
    #         'debit': debit_value if debit_value > 0 else 0,
    #         'credit': -debit_value if debit_value < 0 else 0,
    #         'account_id': debit_account_id,
    #     }

    #     credit_line_vals = {
    #         'name': description,
    #         'product_id': self.product_id.id,
    #         'quantity': qty,
    #         'product_uom_id': self.product_id.uom_id.id,
    #         'ref': description,
    #         'partner_id': partner_id,
    #         'credit': credit_value if credit_value > 0 else 0,
    #         'debit': -credit_value if credit_value < 0 else 0,
    #         'account_id': credit_account_id,
    #     }

    #     rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
    #     if credit_value != debit_value:
    #         # for supplier returns of product in average costing method, in anglo saxon mode
    #         diff_amount = debit_value - credit_value
    #         price_diff_account = self.product_id.property_account_creditor_price_difference

    #         if not price_diff_account:
    #             price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
    #         if not price_diff_account:
    #             raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

    #         rslt['price_diff_line_vals'] = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': description,
    #             'partner_id': partner_id,
    #             'credit': diff_amount > 0 and diff_amount or 0,
    #             'debit': diff_amount < 0 and -diff_amount or 0,
    #             'account_id': price_diff_account.id,
    #         }
    #     return rslt