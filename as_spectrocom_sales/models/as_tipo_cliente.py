from odoo import models, fields, api

class TipoCliente(models.Model):
    _name="as.tipo.cliente"
    _description="Tipo de Cliente"

    name = fields.Char(string="Tipo de cliente", required=True)
    dias_credito = fields.Integer('Dias de credito', help=u"Dias de credito para la venta.", required=True)

    cliente = fields.Boolean(string="Cliente", default=False)
    proveedor = fields.Boolean(string="Proveedor", default=False)