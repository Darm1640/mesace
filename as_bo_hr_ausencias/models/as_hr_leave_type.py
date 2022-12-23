# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_round, float_compare

class HrEmployee(models.Model):
    _inherit = 'hr.leave.type'
    
    as_calculo_vaca = fields.Boolean(string="Calculo de vacaciones")
    as_motivo_permiso = fields.Boolean(string="Motivos de Permiso")

    # @api.model
    # def create(self,vals):
    #     res = super(HrEmployee, self).create(vals)
    #     regsitros =self.env['as.employee.bonus'].sudo().search([('as_date_start', '>=', res.date_from),('as_date_end', '<=', res.date_to),('employee_id', '=', res.employee_id.id),('as_modalidad', '=', 'auto'),('state', '=', 'dapproved_hr_manager')])
    #     if regsitros:
    #         bono_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','INGRESOS03')])
    #         bono_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','INGRESOS03')])
    #         discount_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','OTRDES3')])
    #         discount_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','OTRDES3')])
    #         for inp in regsitros:
    #             if inp.as_tipo == 'bonus':
    #                 vals = {
    #                     'payslip_id':res.id,
    #                     'input_type_id':bono_automatico_type.id,
    #                     'amount': inp.bonus_amount,
    #                     'as_bonus_discount_id': inp.id,
    #                     'as_type_id': bono_automatico.id,
    #                 }
    #                 self.env['hr.payslip.input'].sudo().create(vals)
    #                 inp.as_state_payroll = 'asign'
    #                 inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(res.name), content_subtype='html')  
    #             else:
    #                 vals = {
    #                     'payslip_id':res.id,
    #                     'input_type_id':discount_automatico_type.id,
    #                     'amount': inp.bonus_amount,
    #                     'as_bonus_discount_id': inp.id,
    #                     'as_type_id': discount_automatico.id,
    #                 }
    #                 self.env['hr.payslip.input'].sudo().create(vals)
    #                 inp.as_state_payroll = 'asign'
    #                 inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(res.name), content_subtype='html')  
    #     return res

    # def action_payslip_done(self):
    #     res = super(HrEmployee, self).action_payslip_done()
    #     for payslip in self:
    #         for line in payslip.input_line_ids:
    #             if line.as_bonus_discount_id:
    #                 line.as_bonus_discount_id.as_state_payroll = 'done'
    #                 line.as_bonus_discount_id.state = 'edone'
    #     return res

    # def action_payslip_cancel(self):
    #     res = super(HrEmployee, self).action_payslip_cancel()
    #     for payslip in self:
    #         for line in payslip.input_line_ids:
    #             if line.as_bonus_discount_id:
    #                 line.as_bonus_discount_id.as_state_payroll = 'draft'
    #                 line.as_bonus_discount_id.state = 'dapproved_hr_manager'
    #     return res