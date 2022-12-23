# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AsinstructiveSale(models.Model):
    """Modelo encargado de guardar las Instructiva de trabajo para Espectrocom"""
    _name="as.instructive.sale.2"
    _description="Modelo encargado de guardar las Instructiva de trabajo almacenable para Espectrocom"

    sequence = fields.Integer(string='Item')
    sequence_2 = fields.Char(string='Item')
    name = fields.Char(string='Campo')
    as_template_id = fields.Many2one('as.template.project', string='Código',copy=False)
    as_type_id = fields.Many2one('as.type.service', string='Tipos de Servicio')
    as_partner_id = fields.Many2one('res.partner', string='Cliente')
    as_product_id = fields.Many2one('product.product', string='Producto')
    as_lugar = fields.Char(string='Lugar')
    as_fecha_planificada = fields.Date(string='Fecha Planificada')
    as_presupuesto_planificado = fields.Float(string='Presupuesto Planificado')
    as_duration = fields.Integer(string='Duración')
    as_duration_type = fields.Selection([
        ('1', 'Dia'),
        ('2', 'Mes'),
        ('3', 'Año'),
    ], default=False, string="Tipo Duración del Proyecto")
    as_sale_id = fields.Many2one('sale.order', string='Venta')
    as_note = fields.Text(string='Descripción del proyecto')

    as_nombre_item = fields.Char(string='Nombre item')
    as_numero_parte = fields.Char(string='Numero de parte')
    as_modelo = fields.Char(string='Modelo')
    as_marca = fields.Char(string='Marca')
    as_unidad = fields.Char(string='Unidad')
    as_cant = fields.Char(string='Cantidad')