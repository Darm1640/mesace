# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Contracttc(models.Model):
    _name = 'hr.subtipo.cotizante'
    _order = 'code, id'
    _description = 'subtipo cotizante'
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)


class Contracttp(models.Model):
    _name = 'hr.tipo.cotizante'
    _order = 'code, id'
    _description = 'tipo cotizante'
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)

class Contracth(models.Model):
    _name = 'hr.contract.historial'
    _order = 'code, id'
    _description = 'contract historial'
    novedades_ids = fields.Many2one('hr.novedades.pila', required=True, help="Name")

class Contractnop(models.Model):
    _name = 'hr.novedades.code'
    _order = 'code, id'
    _description = 'Novedades'
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)

class ContractTn(models.Model):    
    _name = 'hr.novedades.pila'
    _description = 'Pila'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    date = fields.Date(help="Gives the sequence when displaying a list of Contract.", default=10)
    employee_id = fields.Many2one('hr.employee', required=True, help="Name")
    novedad_id = fields.Many2one('hr.novedades.code', required=True, help="Name")    
    partner_dest_id = fields.Many2one('res.partner', required=True, help="Name")   
    partner_origin_id = fields.Many2one('res.partner', required=True, help="Name")       


