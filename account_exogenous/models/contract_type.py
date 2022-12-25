# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Contracttc(models.Model):
    _name = 'account.activity.economic'
    _order = 'code, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)


class Contracttp(models.Model):
    _name = 'account.campos.formato'
    _order = 'code, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    referencia = fields.Char(string='Contract Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    tipo_id = fields.Many2one('account.tipos.campo', required=True, help="Name")


class Contracth(models.Model):
    _name = 'account.conceptos'
    _order = 'code, id'
    porcentaje_no_deducible = fields.Char(string='Contract Type', required=True, help="Name")
    name = fields.Char(string='Contract Type', required=True, help="Name")
    tope = fields.Char(string='Contract Type', required=True, help="Name")
    referencia = fields.Char(string='Contract Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    form_dian_id = fields.Many2one('account.formato.dian', required=True, help="Name")

class Contracth(models.Model):
    _name = 'account.conceptos.rel'
    _order = 'code, id'
    
    porcentaje_no_deducible = fields.Char(string='Contract Type', required=True, help="Name")
    name = fields.Char(string='Contract Type', required=True, help="Name")
    tope = fields.Char(string='Contract Type', required=True, help="Name")
    referencia = fields.Char(string='Contract Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    form_dian_id = fields.Many2one('account.formato.dian', required=True, help="Name")

class Contracth(models.Model):
    _name = 'account.condiciones.especiales'
    _order = 'code, id'
    
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Char(string='Contract Type', required=True, help="Name")
    
class Contractnop(models.Model):
    _name = 'account.formato.dian'
    _order = 'code, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)

class Contractnop(models.Model):
    _name = 'account.type.ident'
    _order = 'code, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)

class ContractTn(models.Model):    
    _name = 'account.tipos.campo'
    
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)

class ContractTn(models.Model):    
    _name = 'account.tipos.valor'
    
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
class ContractTn(models.Model):    
    _name = 'account.tipos_de_vinculacion'
    
    name = fields.Char(string='Contract Type', required=True, help="Name")
    code = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    


