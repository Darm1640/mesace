# -*- coding: utf-8 -*-
import logging
import odoo
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _

class As_tipo_de_compra(models.Model):
    _name = 'as.tipo.compra'
    _description = "Tipo de compra"

    name = fields.Char('Nombre')
    as_valor_tipo_compra = fields.Char('Valor')