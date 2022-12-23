# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class HrEmployeeSmn(models.Model):
    _name = 'as.hr.smn'

    as_fecha = fields.Datetime(string="A partir de ", default=datetime.now(), required=True)
    name = fields.Char(string="Normativa (Decreto) ")
    amount = fields.Float(string="Monto en Bs.")
    porcentaje = fields.Char(string="%")
    state = fields.Selection([('V','Vigente'),('C','Caducado')], default='C',string='Estado')

    @api.onchange('state')
    def concatenar_nombres(self):
        smns =self.env['as.hr.smn'].sudo().search([('state', '=', 'V')])
        cantidad = len(smns)
        if self.state == 'V':
            cantidad += 1
        if cantidad > 1:
            raise UserError(_('No pueden haber mas de un Sueldo Minimos Nacional en Vigencia, marque como caducado el vigente'))

    @api.model
    def create(self,vals):
        self.concatenar_nombres()
        res = super(HrEmployeeSmn, self).create(vals)
        return res

