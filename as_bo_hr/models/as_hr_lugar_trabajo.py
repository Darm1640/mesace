# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class HrEmployeeLugar_trabajo(models.Model):
    _name = 'as.hr.lugar.trabajo'

    name = fields.Char(string="Nombre Del Lugar de Trabajo")
    as_nro_patronal= fields.Char(string="Numero Patronal")
    as_ciudad = fields.Char(string='Ciudad')
    as_codigo_sucursal = fields.Selection([('0','0'),('2','2')],string='Codigo Sucursal')
   

    # @api.onchange('state')
    # def concatenar_nombres(self):
    #     smns =self.env['as.hr.lugar.trabajo'].sudo().search([('state', '=', 'V')])
    #     cantidad = len(smns)
    #     if self.state == 'V':
    #         cantidad += 1
    #     if cantidad > 1:
    #         raise UserError(_('No pueden haber mas de un Sueldo Minimos Nacional en Vigencia, marque como caducado el vigente'))

    # @api.model
    # def create(self,vals):
    #     self.concatenar_nombres()
    #     res = super(HrEmployeeLugar_trabajo, self).create(vals)
    #     return res

