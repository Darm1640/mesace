# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time

import logging
_logger = logging.getLogger(__name__)

class AsCajaChica(models.Model):
    _inherit = 'as.caja.chica'

    @api.onchange('as_tipo_retencion','as_tipo_documento','as_tipo_factura','product_name_id')
    def as_get_retencion_invoice(self):
        for inv in self:
            if inv.as_tipo_retencion.as_taxes_ids.ids != []:
                inv.as_tax_ids = inv.as_tipo_retencion.as_taxes_ids.ids
            elif inv.as_tipo_factura.as_taxes_ids.ids != []:
                inv.as_tax_ids = inv.as_tipo_factura.as_taxes_ids.ids
            elif self.as_tipo_documento !='Factura':
                inv.as_tax_ids = False
            else:
                inv.as_tax_ids = inv.product_id.supplier_taxes_id.ids

    #crear factura de importacion
    def action_create_invoice(self):
        self.as_partner_id.as_tasas = self.as_tasas
        self.as_partner_id.as_interes = self.as_interes/self.as_amount
        res = super(AsCajaChica, self).action_create_invoice()
        return res