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
    _name = 'as.siat.log'
    _description = "Registro de log de las operaciones enviadas al API"

    name = fields.Char(string="Actión")
    as_user_id = fields.Many2one('res.users', string="Usuario")
    as_success = fields.Boolean(string="Suceso")
    as_estado = fields.Char(string="Estado")
    as_info = fields.Char(string="Información")
    as_json = fields.Char(string="JSON enviado")
    as_json_recibido = fields.Char(string="JSON Recibido")
    as_xml = fields.Char(string="XML recibido")
    as_date = fields.Datetime(string="Fecha", default=fields.Datetime.now())

