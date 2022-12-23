# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import base64
import logging
_logger = logging.getLogger(__name__)

class Ahorasoftplanillatxt(models.TransientModel):
    _name = "as.payslip.txt"
    _description = "Report payslip Report AhoraSoft"

    payslip_run_id = fields.Many2one('hr.payslip.run', string="Nomina",required=True)

    def export_xls(self):
        filename = self.payslip_run_id.name+'.txt'
        fila_facilito = ""
        saltopagina = "\n"
        for slip in self.payslip_run_id.slip_ids:
            nro_cuenta = slip.employee_id.bank_account_id.acc_number
            liquido = self.get_total_rules(slip.id,'TOTAL',slip.employee_id.id,slip.contract_id.id)
            glosa = 'pago sueldo '+self.payslip_run_id.name+' '+ slip.employee_id.nombre+' '+slip.employee_id.apellido_1
            if nro_cuenta:
                fila_facilito += nro_cuenta+'@'+str(round(liquido,2))+'@'+glosa+saltopagina

        id_file = self.env['txt.extended'].create({'as_txt_file': base64.encodestring(bytes(fila_facilito, 'utf-8')), 'as_file_name': filename,'as_txt_file': base64.encodestring(bytes(fila_facilito, 'utf-8'))})
        return {
            'view_mode': 'form',
            'res_id': id_file.id,
            'res_model': 'txt.extended',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0    
