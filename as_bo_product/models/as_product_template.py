# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    """modelo heredado para agregar funcionalidad de generacion de codigo de productos manual o automatico"""
    _inherit = 'product.template'
  
    as_referencia = fields.Boolean(string='Referencia Automática')
    barcode = fields.Char(string='Codigo de Barras')


    @api.onchange('as_contenedor')
    def as_get_contenedor(self):
        for product in self:
            product.as_contenedor_type = product.as_contenedor.as_type.id


    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            if 'as_referencia' in vals_product:
                if vals_product['as_referencia']:
                    secuence =  self.env['ir.sequence'].next_by_code('as.product.code')
                    secuence_name = secuence
                    vals_product['default_code'] = secuence_name
                    vals_product['barcode'] = secuence_name
        templates = super(ProductTemplate, self).create(vals_list)
        return templates

    def write(self, vals):
        for template in self:
            if 'as_referencia' in vals:
                if vals['as_referencia']:
                    secuence =  template.env['ir.sequence'].next_by_code('as.product.code')
                    secuence_name = secuence
                    vals['default_code'] = secuence_name
                    vals['barcode'] = secuence_name
        res = super(ProductTemplate, self).write(vals)
        return res

class ProductProduct(models.Model):
    """modelo heredado para agregar funcionalidad de generacion de codigo de productos manual o automatico"""
    _inherit = 'product.product'
  
    as_referencia_manual = fields.Boolean(string='Referencia Manual', default=True)
    default_code = fields.Char(string='Referencia Interna')

    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            if 'as_referencia_manual' in vals_product:
                if vals_product['as_referencia_manual']:
                    secuence =  self.env['ir.sequence'].next_by_code('as.product.code')
                    secuence_name = secuence
                    vals_product['default_code'] = secuence_name
                    vals_product['barcode'] = secuence_name
        templates = super(ProductProduct, self).create(vals_list)
        return templates

    def write(self, vals):
        for template in self:
            if 'as_referencia_manual' in vals:
                if vals['as_referencia_manual']:
                    secuence =  template.env['ir.sequence'].next_by_code('as.product.code')
                    secuence_name = secuence
                    vals['default_code'] = secuence_name
                    vals['barcode'] = secuence_name
        res = super(ProductProduct, self).write(vals)
        return res
