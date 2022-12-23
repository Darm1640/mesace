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

class as_siat_enpoint(models.Model):
    _name = 'as.siat.endpoint'
    _description = "Registro del Endpoint para comunicacion con el API"

    name  = fields.Char(string="URL Post")
    as_type = fields.Selection([
        ('Token','Token'),
        ('CUIS','CUIS'),
        ('PDV','PDV'),
        ('NIT','NIT'),
        ('CierrePDV','CierrePDV'),
        ('CUFD','CUFD'),
        ('Catalogos','Catalogos'),
        ('Factura','Factura'),
        ('Factura Electronica','Factura Electronica'),
        ('Recepción de Factura','Recepción de Factura'),
        ('Cancelar Factura','Cancelar Factura'),
        ('NDC','NDC'),
        ('Recepción de NDC','Recepción de NDC'),
        ('Cancelar NDC','Cancelar NDC'),
        ('Recepción Envio Masivo','Recepción Envio Masivo'),
        ('Validación Envio Masivo','Validación Envio Masivo '),
        ('Crear Contingencia','Crear Contingencia'),
        ('Recepción Envio Contingencia','Recepción Envio Contingencia'),
        ('Validación Envio Contingencia','Validación Envio Contingencia'),
        ('Consultar Cliente','Consultar Cliente'),
        ('Verifica Comunicación','Verifica Comunicación'),
        ('Factura Consulta','Factura Consulta'),
        ('Factura Cancelar','Factura Cancelar'),
        ], string='Tipo', default='Factura')
