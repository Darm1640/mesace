# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AsProductAssets(models.Model):
    """modelo heredado para agregar custodios de activos fijos"""
    _name = 'as.assets.custodies'
    _description = "modelo heredado para agregar custodios de activos fijos"

    as_date_start = fields.Date(string='Fecha Inicial')
    as_date_end = fields.Date(string='Fecha Final')
    as_employee_id = fields.Many2one('hr.employee',string='Custodio')
    as_job_id = fields.Many2one('hr.job',string='Puesto de Trabajo')
    as_department_id = fields.Many2one('hr.department',string='Departamento')
    as_location_id = fields.Many2one('stock.location',string='Ubicación')
    as_product_activo_id = fields.Many2one('account.asset.asset',string='Producto')

    @api.onchange('as_employee_id')
    def as_get_job(self):
        for cust in self:
            cust.as_job_id = cust.as_employee_id.job_id.id
            cust.as_department_id = cust.as_employee_id.department_id.id
            
class ProductTemplate(models.Model):
    """modelo heredado para agregar funcionalidad de activo tangible relacionado"""
    _inherit = 'product.template'
  
    as_assets = fields.Many2one('product.template',string='Activo Relacionado',domain="[('asset_category_id', '!=', False), ('type', '=', 'service')]")

class account_asset_asset(models.Model):
    """modelo heredado para agregar funcionalidad de activo tangible relacionado"""
    _inherit = 'account.asset.asset'
  
    as_custodies_lines = fields.One2many('as.assets.custodies','as_product_activo_id',string='Custodios')
