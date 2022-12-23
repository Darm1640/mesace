# -*- coding: utf-8 -*-
##############################################################################

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

# Requests a la pagina de Impuestos Nacionales Bolivia
import requests
from lxml import etree, objectify
from bs4 import BeautifulSoup
import logging
_logger = logging.getLogger(__name__)

class AhorasoftCUFD(models.Model):
    _name = 'as.siat.cufd'
    _description = "Registro del CUFD para que pueda ser localizado mediante consulta"
    _order = "as_expire_date desc"

    active = fields.Boolean(string="Activo",default=True)

    as_cufd_value = fields.Char(string="CUFD")
    as_control_code = fields.Char(string="Codigo de control")
    as_expire_date = fields.Char(string="Fecha de vigencia")
    as_address = fields.Char(string="Dirección")
    as_branch_office = fields.Many2one('as.siat.sucursal', string="Sucursal")
    as_pdv_id = fields.Many2one('as.siat.punto.venta', string="Punto de Venta")


class AhorasoftPDV(models.Model):
    _name = 'as.siat.punto.venta'
    _description = "Registro del CUFD para que pueda ser localizado mediante consulta"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre")
    active = fields.Boolean(string="Activo",default=True)
    as_code = fields.Char(string="Código")
    as_cuis = fields.Char(string="CUIS")
    as_cufd = fields.One2many('as.siat.cufd', 'as_pdv_id', string="CUFD")
    as_branch_office = fields.Many2one('as.siat.sucursal', string="Sucursal")
    as_type = fields.Many2one('as.siat.catalogos', string="Tipo Punto de venta", domain="[('as_group.name', '=', 'PUNTO_VENTA')]", required=True, default=lambda self: self.env['as.siat.catalogos'].search([('as_group.name', '=', 'PUNTO_VENTA')],limit=1))
    
    def as_request_point_sale_close(self):
        pass
