# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class as_product_product(models.Model):
    _inherit = 'product.product'

    def _get_description(self,picking_type_id):
        res = super(as_product_product, self)._get_description(picking_type_id)
        if self:
            self.ensure_one()
            picking_code = picking_type_id.code
            description = self.description or self.name
            if picking_code == 'incoming':
                return self.description_pickingin or description
            if picking_code == 'outgoing':
                return self.description_pickingout or self.name
            if picking_code == 'internal':
                return self.description_picking or description