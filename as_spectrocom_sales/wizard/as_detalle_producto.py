# -*- coding: utf-8 -*-
##############################################################################

from datetime import datetime, timedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.exceptions import UserError
from odoo.tools.translate import _
import base64
from odoo import netsvc
from odoo import tools
from time import mktime
import logging
from datetime import datetime
from odoo import api, fields, models

class as_product_detail_wiz(models.TransientModel):
    _inherit="as.product.detail.wiz"
    _description = "Warehouse Reports by AhoraSoft"
    
    as_bussiness_id = fields.Many2one('as.business.unit', string='Unidad de Negocio')


