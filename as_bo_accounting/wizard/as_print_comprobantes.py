# -*- coding: utf-8 -*-
##############################################################################
from odoo import api, fields, models
import time
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.tools.translate import _
import base64
from odoo import netsvc
from odoo import tools
from time import mktime

import logging
_logger = logging.getLogger(__name__)

# modelo de regeneracion de codigo/numeracion del comprobante
class as_printer_account(models.TransientModel):
    _name = "as.printer.account"
    _description = "Regenerar sequencia de comprobante"
    
    as_start_date  = fields.Date(string="Fecha Inicio", default=fields.Date.context_today, required=True)
    as_end_date = fields.Date(string="Fecha Final",  default=fields.Date.context_today, required=True)
    as_journal_id = fields.Many2one('account.journal',string='Serie/Diario')
    # as_secuencia = fields.Many2one('ir.sequence', string='Secuencia Diario')

    # Boton regenerar secuencia 
    # @api.multi
    def printer_sequencia(self):
        move_obj = self.env['account.move']
        # obtiene todos los comprobantes de la fecha ejmpelo "junio 2018"
        filtro_query = ''
        # if self.as_journal_id:
        #     filtro_query += "AND am.journal_id = "+str(self.as_journal_id.id)

        # if self.as_secuencia:
        #     filtro_query += "AND am.secuencia = "+str(self.as_secuencia.id)
            
        query_ids = ("""
            SELECT
                am.id  
            FROM
                account_move am
            WHERE
                am.date >='"""+str(self.as_start_date)+"""' and am.date <= '"""+str(self.as_end_date)+"""'
                """+filtro_query+"""
        """)
        
        _logger.debug("\n\n Query 3 asientos %s\n\n",query_ids)

        self.env.cr.execute(query_ids)

        product_categories = [j for j in self.env.cr.fetchall()]

        return self.env.ref('as_bo_accounting.action_report_account_receipt_bo_accounting').report_action(product_categories) 