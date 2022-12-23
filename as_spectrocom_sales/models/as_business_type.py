from odoo import models, fields, api

class AsBusinessUnit(models.Model):
    """Modelo encargado de guardar los tipos de unidad de negocio para Espectrocom"""
    _name="as.business.unit"
    _description="Modelo encargado de guardar los tipos de unidad de negocio para Espectrocom"

    name = fields.Char(string='Nombre')
    as_type_ids = fields.One2many('as.type.service', 'as_bussiness_id', string='Tipos de Servicio')

class AsTypeService(models.Model):
    """Modelo encargado de guardar los tipos de servicio para unidades de negocio para Espectrocom"""
    _name="as.type.service"
    _description="Modelo encargado de guardar los tipos de unidad de negocio para Espectrocom"

    name = fields.Char(string='Nombre')
    as_bussiness_id = fields.Many2one('as.business.unit', string='Unidad de Negocio')

