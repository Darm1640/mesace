from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class as_stock_picking(models.Model):
    _inherit = 'stock.picking'

    as_generate_assets = fields.Boolean('Generado Activo',copy=False)
    

    def action_create_assets(self):
        for inv in self:
            for mv_line in inv.move_line_ids_without_package:
                if mv_line.as_asset_category_id:
                    mv_line.asset_create()
        return True

    def action_update_sale(self):
        for inv in self:
            if inv.state == 'done':
                for line_move in inv.move_line_ids_without_package:
                    if line_move.lot_id:
                        assets = self.env['account.asset.asset'].sudo().search([('as_lot_id','=',line_move.lot_id.id)],limit=1)
                        if assets:
                            assets.as_sale = line_move.move_id.sale_line_id.order_id
                            if line_move.move_id.sale_line_id:
                                assets.as_value = line_move.move_id.sale_line_id.price_unit * line_move.move_id.sale_line_id.product_uom_qty
                                assets.as_process_sale()
                                line_move.as_asset_sale = True
                
            else:
                raise UserError(_('El movimiento dee estar en estado Hecho.'))


class as_stock_move(models.Model):
    _inherit = "stock.move.line"
    _description = "lineas de movimiento de inventario"

    as_account_id = fields.Many2one('account.asset.category', string='Asset Category')
    as_asset_category_id = fields.Many2one('account.asset.category', string='Asset Category')
    as_asset_start_date = fields.Date(string='Asset Start Date', compute='_get_asset_date', readonly=True, store=True)
    as_asset_end_date = fields.Date(string='Asset End Date', compute='_get_asset_date', readonly=True, store=True)
    as_asset_mrr = fields.Float(string='Monthly Recurring Revenue', compute='_get_asset_date', readonly=True,
                             digits="Account", store=True)
    as_asset_sale = fields.Boolean('Vendido AF',copy=False)

    @api.depends('as_asset_category_id', 'picking_id.date_done')
    def _get_asset_date(self):
        for rec in self:
            rec.as_asset_mrr = 0
            rec.as_asset_start_date = False
            rec.as_asset_end_date = False
            cat = rec.as_asset_category_id
            if cat:
                if cat.method_number == 0 or cat.method_period == 0:
                    raise UserError(_('The number of depreciations or the period length of '
                                      'your asset category cannot be 0.'))
                months = cat.method_number * cat.method_period
                if rec.picking_id.move_type in ['out_invoice', 'out_refund']:
                    rec.as_asset_mrr = (rec.move_id.price_unit*rec.move_id.product_uom_qty) / months
                if rec.picking_id.date_done:
                    start_date = rec.picking_id.date_done.replace(day=1)
                    end_date = (start_date + relativedelta(months=months, days=-1))
                    rec.as_asset_start_date = start_date
                    rec.as_asset_end_date = end_date

    def asset_create(self):
        if self.as_asset_category_id:
            if not self.as_asset_category_id.as_sequence_id:
                raise UserError(_('La categoria del Activo debe tener una secuencia seleccionada.'))
            codigo =  self.as_asset_category_id.as_sequence_id.next_by_id()
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

    @api.onchange('as_asset_category_id')
    def onchange_asset_category1_id(self):
        self.as_account_id = self.as_asset_category_id.account_asset_id.id

    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        self.onchange_asset_category1_id()

    @api.onchange('product_id')
    @api.depends('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.as_asset_category_id = rec.product_id.product_tmpl_id.asset_category_id

