# -*- coding: utf-8 -*-
##############################################################################
import time
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.tools.translate import _
import base64
from odoo import api, fields, models
from odoo import netsvc
from odoo import tools
from time import mktime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

# modelo de regeneracion de codigo/numeracion del comprobante
class rm_asiento_apertura(models.TransientModel):
    _name = "as.regenerar.sequencia"
    _description = "Regenerar sequencia de comprobante"

    MESES = [('01',"Enero"),
        ("02",'Febrero'),
        ('03','Marzo'),
        ('04','Abril'),
        ('05','Mayo'),
        ('06','Junio'),
        ('07','Julio'),
        ('08','Agosto'),
        ('09','Septiembre'),
        ('10','Octubre'),
        ('11','Noviembre'),
        ('12','Diciembre')]

    date_year = fields.Selection([(str(num), str(num)) for num in range(2020, (datetime.now().year)+1 )], string='Fecha', required=True,default=datetime.now().year)
    date_month = fields.Selection(MESES,string='Fecha mes', required=True)
    journal_id = fields.Many2one('account.journal',string='Serie/Diario')
    as_secuencia = fields.Many2one('ir.sequence', string='Secuencia Diario')
    as_contable = fields.Boolean(string='Facturas sin asientos')

    # Boton regenerar secuencia 
    
    def regenerar_sequencia(self):
        move_obj = self.env['account.move']
        fecha = str(self.date_year)+'-'+self.date_month
        # obtiene todos los comprobantes de la fecha ejmpelo "junio 2018"
        filtro_query = ''
        if self.journal_id:
            filtro_query += "AND am.journal_id = "+str(self.journal_id.id)

        if self.as_secuencia:
            filtro_query += "AND am.as_secuencia_id = "+str(self.as_secuencia.id)

        if self.as_contable:
            filtro_query += "and as_contable = True"
        else:
            filtro_query += " AND as_contable != True"
            
        self._cr.execute("""
            SELECT
                am.id,
                am.NAME,
                am.date,
                aj.sequence_id
            FROM
                account_move am
                JOIN account_journal aj ON aj.id = am.journal_id 
            WHERE
                to_char ( am.date, 'YYYY-MM' ) = '"""+str(fecha)+"""'
                
                """+filtro_query+"""
            ORDER BY
                am.date ASC
            """)

        res_query = self._cr.fetchall()
        # obtiene la secuencia del tipo de diario/comprobante
        if not self.as_contable:
            if self.journal_id:
                if self.journal_id.sequence_id:
                    sequence_obj = self.journal_id.sequence_id
                else:
                    raise UserError(_('Por favor defina una sequencia al tipo de diario.'))
            if self.as_secuencia:
                sequence_obj = self.as_secuencia
        else:
            if self.journal_id:
                if self.journal_id.as_sequence_wa_id:
                    sequence_obj = self.journal_id.as_sequence_wa_id
                else:
                    raise UserError(_('Por favor defina una sequencia al tipo de diario.'))
            if self.journal_id.as_sequence_wa_id:
                sequence_obj = self.journal_id.as_sequence_wa_id
        # actualiza la secuencia del tipo de comprobante a UNO "1"
        if sequence_obj.use_date_range:
            self._cr.execute("""
                UPDATE ir_sequence_date_range SET number_next=1
                WHERE sequence_id = %s AND date_from <= %s AND date_to >= %s
                """,(sequence_obj.id,fecha+'-01',fecha+'-01',))
            # seq_date = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.journal_id.sequence_id.id), ('date_from', '<=', fecha+'-01'), ('date_to', '>=', fecha+'-01')], limit=1)
        else:
            sequence_obj.update({'number_next_actual':1})
        # El resultado de la consulta realiza el recorrido y va generando la numeracion/codigo del comprobante 
        for x in res_query:
            comprobante = move_obj.browse(x[0])
            new_name = sequence_obj.with_context(ir_sequence_date=x[2]).next_by_id()
            comprobante.name = new_name
            # _logger.info('\n\n Comprobante actualizado codigo anterior: %r   		codigo actual: %s\n\n',x[1],new_name)