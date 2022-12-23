from odoo import models, fields, api

class AsPoposalAux(models.Model):
    """Modelo encargado de guardar las condiciones de propuesta para Espectrocom reparaciones"""
    _name="as.proposal.aux"
    _description="Modelo encargado de guardar las condiciones de propuesta para Espectrocom"

    name = fields.Char(string='Campo')
    as_note = fields.Char(string='Observaciones')
    as_conditions_lines = fields.One2many('as.proposal.conditions.aux', 'as_proposal_aux_id', string='Linea de Condiciones')

class AsPoposalConditions(models.Model):
    """Modelo encargado de guardar las condiciones de propuesta lineas con campos para Espectrocom"""
    _name="as.proposal.conditions.aux"
    _description="Modelo encargado de guardar las condiciones de propuesta para Espectrocom"

    name = fields.Char(string='Campo')
    as_valor = fields.Char(string='Valor Inicial')
    as_valor_2 = fields.Char(string='Valor Final')
    as_proposal_aux_id = fields.Many2one('as.proposal.aux', string='Venta')

class AsBusinessUnit(models.Model):
    """Modelo encargado de guardar las condiciones de propuesta para Espectrocom"""
    _name="as.proposal.conditions.sale.aux"
    _description="Modelo encargado de guardar las condiciones de propuesta para Espectrocom"

    name = fields.Char(string='Campo')
    as_valor = fields.Char(string='Valor Inicial')
    as_valor_2 = fields.Char(string='Valor Final')
    as_sale_id = fields.Many2one('sale.order', string='Venta')
    as_proposal_id = fields.Many2one('as.proposal.aux', string='Venta')