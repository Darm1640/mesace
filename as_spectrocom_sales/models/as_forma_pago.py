from odoo import models, fields, api

class TipoCliente(models.Model):
    _name="as.forma.pago"
    _description="Forma de Pago"

    name = fields.Char('Forma de Pago', required=True)
    compra = fields.Boolean('Compra', default=False, help='Visible en formulario de compra')
    venta = fields.Boolean('Venta', default=False, help='Visible en formulario de venta')