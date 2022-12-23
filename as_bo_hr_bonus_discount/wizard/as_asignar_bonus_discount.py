# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import re
import xlrd
from xlrd import open_workbook
import base64
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
_logger = logging.getLogger(__name__)

class as_asignar_bonus_discount(models.Model):
    _name="as.asignar.bonus.discount"
    _description="Asignar Bonos o descuentos"

    as_playslip_run_id = fields.Many2one('hr.payslip.run', string='Procesamiento de Nomina',domain="[('state','in',('draft','verify'))]")

    def actualizar_costos_productos(self):
        self.ensure_one()
        context = self._context
        regsitros = self.env[context['active_model']].search([('id','in',tuple(self._context['active_ids']))])
        bono_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','INGRESOS02')])
        bono_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','INGRESOS02')])
        discount_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','OTRDES2')])
        discount_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','OTRDES2')])
        for slip in self.as_playslip_run_id.slip_ids:
            for inp in regsitros:
                if inp.employee_id == slip.employee_id:
                    if slip.date_from != inp.as_date_start:
                        raise ValidationError(_("Fechas de bono o descuento no coinciden con la nomina seleccionada."))
                    if inp.as_tipo == 'bonus':
                        vals = {
                            'payslip_id':slip.id,
                            'input_type_id':bono_automatico_type.id,
                            'amount': inp.bonus_amount,
                            'as_bonus_discount_id': inp.id,
                            'as_type_id': bono_automatico.id,
                        }
                        self.env['hr.payslip.input'].sudo().create(vals)
                        inp.as_state_payroll = 'asign'
                        inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(slip.name), content_subtype='html')  
                    else:
                        vals = {
                            'payslip_id':slip.id,
                            'input_type_id':discount_automatico_type.id,
                            'amount': inp.bonus_amount,
                            'as_bonus_discount_id': inp.id,
                            'as_type_id': discount_automatico.id,
                        }
                        self.env['hr.payslip.input'].sudo().create(vals)
                        inp.as_state_payroll = 'asign'
                        inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(slip.name), content_subtype='html')  
                    slip.compute_sheet()

