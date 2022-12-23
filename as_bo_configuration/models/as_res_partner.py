# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Add_Nit(models.Model):
    """ Esta clase agrega los campos razon social y nit a account_move """
    _inherit = 'res.partner'

    as_razon_social = fields.Char(string="Razon Social") 