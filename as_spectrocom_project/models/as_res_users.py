# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64

class ResUsers(models.Model):
    _inherit = "res.users"

    as_aprobar_materiales = fields.Boolean(string="Permitido aprobar Solicitudes de Materiales")