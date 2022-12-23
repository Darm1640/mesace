# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
  
    as_bussiness_id = fields.Many2one('as.business.unit', string='Linea de Negocio')
    as_type_id = fields.Many2one('as.type.service', string='Tipos de Servicio')
    as_nota = fields.Char(string='Nota')
    as_obligatorio_check = fields.Boolean(string="Nro de parte obligatorio", default=True)
    
    @tools.ormcache()
    def _get_default_category_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('product.product_category_all')
    
    categ_id = fields.Many2one('product.category', 'Product Category',
        change_default=True, default=_get_default_category_id, group_expand='_read_group_categ_id',
        required=False, help="Select category for the current product") 
    
    @api.onchange('as_bussiness_id')
    def compute_bussines(self):
        for rec in self:
            return {'domain': {
                'as_type_id': [('id', 'in', rec.as_bussiness_id.as_type_ids.ids)]
            }}
            
    @api.onchange('product_part_num')
    @api.depends('product_part_num')
    def as_onchange_nro_parte(self):
        for sale in self:
            if sale.product_part_num:
                for valor in sale.product_part_num:
                    if valor == '-' or valor == ',' or valor == '.':
                        raise UserError('No se aceptan comas, puntos ni guiones en el campo Nro Parte')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
  
    # as_bussiness_id = fields.Many2one('as.business.unit', string='Unidad de Negocio')
    # as_type_id = fields.Many2one('as.type.service', string='Tipos de Servicio')

    # @api.model
    # @api.depends('product_id')
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     res = super(ProductProduct, self).name_search(name='', args=None, operator='ilike', limit=100)
    #     # ids = self.search(args + ['|',('as_name_ids.as_codigo', '=', name),('as_numero_parte', '=', name),('name', 'ilike', name)], limit=limit)
    #     ids = self.search(args + ['|','|','|','|',('product_part_num', 'ilike', name),('default_code', 'ilike', name),('product_model_id', 'ilike', name), ('name', operator, name), ('name', 'ilike', name)], limit=limit)
    #     array_name = name.split(' ')
    #     valores = []
    #     cont = 1
    #     if len(array_name) > 1:
    #         for value in array_name:
    #             valores.append(('name', 'ilike', value))
    #         ids = self.search(args + valores, limit=limit)
    #     if ids:
    #         return ids.name_get()
    #     return res
 
    @api.onchange('as_bussiness_id')
    def compute_bussines(self):
        for rec in self:
            return {'domain': {
                'as_type_id': [('id', 'in', rec.as_bussiness_id.as_type_ids.ids)]
            }}
