from odoo import models, fields, api
class SaleProduct(models.Model):
    _inherit = 'product.template'
    as_nro_parte_id=fields.Char('Nro parte')
    _sql_constraints = [
                     ('nro_parte', 
                      'unique(as_nro_parte_id)',
                      'el nombre del unico debe ser unico!')]
