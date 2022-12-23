# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsTipoRetencion(models.Model):
    """Para almacenar los tipos de retencion para contabilidad en compras"""
    _name = 'as.tipo.retencion'
    _description = "Retencion"
    _rec_name = 'name'

    name = fields.Char('Nombre retención', help=u'Nombre de retención.')
    as_iue = fields.Float('IUE (%)', help=u'IUE.')
    as_it = fields.Float('IT (%)', help=u'IT.')
    as_iva = fields.Float('IVA (%)', help=u'IVA.')
    tipo_operacion = fields.Char('Tipo Operacion', help=u'Tipo de Operacion')
    as_cuenta_iva = fields.Many2one('account.account', string="Cuenta IVA")
    as_cuenta_it = fields.Many2one('account.account', string="Cuenta IT")
    as_cuenta_iue = fields.Many2one('account.account', string="Cuenta IUE")