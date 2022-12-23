from odoo import api, fields, models, _
from odoo.exceptions import UserError

class res_users(models.Model):
    _inherit = 'res.users'

    as_system_certificate = fields.Many2many('as.siat.codigo.sistema', string="Certificado")
    as_branch_office = fields.Many2many('as.siat.sucursal', string="Sucursal")
    as_pdv_ids = fields.Many2many('as.siat.punto.venta', string="Puntos de Venta")

    