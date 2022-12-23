from odoo import api, models, fields
from odoo import tools

class product_product(models.Model):
    _inherit = 'account.asset.category'

    @api.depends('as_useful_life')
    def _compute_dias_util(self):
        for dias in self:
            dias.as_dias_util = dias.as_useful_life * 365

    as_useful_life = fields.Float(string="Vida Util")
    as_coeficiente = fields.Float(string="Coeficiente(%)")
    as_dias_util = fields.Float(string="Dias de vida util", compute='_compute_dias_util',store=True)
    account_asset_generic_id = fields.Many2one('account.account', string='Cuenta Activo Secundaria', domain=[('internal_type','=','other'), ('deprecated', '=', False)])
    as_modality = fields.Selection([
        ('anual', 'Anual'),
        ('mensual', 'Mensual'),
    ], string="Tipo de Depreciación",default="mensual")
    as_date_inicio = fields.Boolean(string="Ultima fecha del año o mes")
    as_estructura_id = fields.Many2one('as.account.structure', 'Estructura para dar de baja activo')
    as_estructura_assets_id = fields.Many2one('as.account.sale', 'Cuentas Contables para asientos de AF')
    # as_estructura_sale1_id = fields.Many2one('as.account.structure', 'Estructura Asiento 1')
    # as_estructura_sale2_id = fields.Many2one('as.account.structure', 'Estructura Asiento 2')
    # as_estructura_sale3_id = fields.Many2one('as.account.structure', 'Estructura Asiento Caso precio de venta menor a la depreciacion acumulado')
    # as_estructura_sale4_id = fields.Many2one('as.account.structure', 'Estructura Asiento precio de venta mayor a la depreciacion acumulada')
    as_assets_type = fields.Selection([
        ('Tangible', 'Tangible'),
        ('Intangible', 'Intangible'),
    ], string="Tipo de Activo",default="Tangible")

    @api.onchange('as_modality')
    def as_get_assets_modality(self):
        for asset in  self:
            if asset.as_modality == 'anual':
                asset.method_period = 12
            else:
                asset.method_period = 1
