from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    as_confirmar_ventas_sin_stock = fields.Boolean(string="No confirmar ventas sin stock", default=False, help="Permite confirmar ventas que pudieran generar stock negativos.")
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['as_confirmar_ventas_sin_stock'] = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_confirmar_ventas_sin_stock'))
        return res
    
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_confirmar_ventas_sin_stock', self.as_confirmar_ventas_sin_stock)
        super(ResConfigSettings, self).set_values()
    
class sale_order(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super(sale_order,self).action_confirm()
        self.confirm_sale_sctok()
        return result

    def confirm_sale_sctok(self):
        for sale in self:
            as_confirmar_ventas_sin_stock = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_confirmar_ventas_sin_stock'))

            if as_confirmar_ventas_sin_stock:
                for sol in sale.order_line: #sol being sale_order_line
                    if sol.product_id.type != 'service':
                        if sol.as_stock_fisico_actual < sol.product_uom_qty:
                            raise UserError(_("No es posible confirmar una venta sin el stock suficiente.\nRevise sus configuraciones o contacte con su administrador de sistemas."))
        return True