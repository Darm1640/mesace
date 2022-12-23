# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _

# Sucursal
class as_cafc(models.Model):
    _name = 'as.cafc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Modelo que guarda la informacion de los CAFC"

    name = fields.Char(string="Código/Nombre",required=True)
    as_date_start = fields.Date(string="Fecha Inicio",required=True)
    as_date_end = fields.Date(string="Fecha Fin",required=True)
    as_actividad = fields.Many2one('as.siat.catalogos', string="Actividades Económicas", domain="[('as_group', '=', 'ACTIVIDAD_NIT')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'ACTIVIDAD_NIT')],limit=1))
    as_inicio = fields.Integer(string="Rango Inicio",required=True)
    as_fin = fields.Integer(string="Rango Fin",required=True)
    as_proximo = fields.Integer(string="Proximo",required=True)

    @api.onchange('as_inicio')
    def as_get_inicio(self):
        self.as_proximo = self.as_inicio

