from odoo import models, fields, api

class AsPoposalConditions(models.Model):
    """Modelo encargado de guardar las condiciones de propuesta para Espectrocom"""
    _name="as.proposal"
    _description="Modelo encargado de guardar las condiciones de propuesta para Espectrocom"

    name = fields.Char(string='Campo')
    as_note = fields.Char(string='Observaciones')
    as_conditions_lines = fields.One2many('as.proposal.conditions', 'as_proposal_id', string='Linea de Condiciones')


class AsPoposalConditions(models.Model):
    """Modelo encargado de guardar las condiciones de propuesta lineas con campos para Espectrocom"""
    _name="as.proposal.conditions"
    _description="Modelo encargado de guardar las condiciones de propuesta para Espectrocom"

    name = fields.Char(string='Campo')
    as_valor = fields.Char(string='Valor')
    as_proposal_id = fields.Many2one('as.proposal', string='Venta')

class AsBusinessUnit(models.Model):
    """Modelo encargado de guardar las condiciones de propuesta para Espectrocom"""
    _name="as.proposal.conditions.sale"
    _description="Modelo encargado de guardar las condiciones de propuesta para Espectrocom"

    name = fields.Char(string='Campo')
    as_valor = fields.Char(string='Valor')
    as_sale_id = fields.Many2one('sale.order', string='Venta')
    as_proposal_id = fields.Many2one('as.proposal', string='Venta')