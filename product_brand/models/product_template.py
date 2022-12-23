# Copyright 2009 NetAndCo (<http://www.netandco.net>).
# Copyright 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>
# Copyright 2014 prisnet.ch Seraphine Lantible <s.lantible@gmail.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Daniel Campos <danielcampos@avanzosc.es>
# Copyright 2019 Kaushal Prajapati <kbprajapati@live.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_brand_id = fields.Many2one(
        "product.brand", string="Brand", help="Select a brand for this product"
    )
    product_model_id = fields.Many2one(
        "product.model", string="Modelo", help="Seleccione un modelo para este producto"
    )
    product_part_num = fields.Char('Nro Parte')
    
    _sql_constraints = [
        ('unique_reference', 'unique(default_code)', "El código de referencia interna ya ha sido asignado a otro producto!"),
    ]
    _sql_constraints = [
        ('unique_part_product', 'unique(product_part_num)', "El número de parte ya ha sido asignado a otro producto!"),
    ]           
   