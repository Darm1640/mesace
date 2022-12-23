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
    _inherit = 'hr.payslip'
    
    @api.model
    def create(self,vals):
        res = super(HrEmployee, self).create(vals)
        regsitros =self.env['as.employee.bonus'].sudo().search([('as_date_start', '>=', res.date_from),('as_date_start', '<=', res.date_to),('employee_id', '=', res.employee_id.id),('as_modalidad', '=', 'auto'),('state', '=', 'dapproved_hr_manager')])
        if regsitros:
            bono_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','INGRESOS03')])
            bono_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','INGRESOS03')])
            discount_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','OTRDES3')])
            discount_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','OTRDES3')])
            self.input_line_ids.filtered(lambda r: r.input_type_id in (bono_automatico_type.id,discount_automatico_type.id)).unlink()
            for inp in regsitros:
                existe =self.env['hr.payslip.input'].sudo().search([('payslip_id', '=', res.id),('as_bonus_discount_id', '=', inp.id)])
                existe.unlink()
                if inp.as_tipo == 'bonus':
                    vals = {
                        'payslip_id':res.id,
                        'input_type_id':bono_automatico_type.id,
                        'amount': inp.bonus_amount,
                        'as_bonus_discount_id': inp.id,
                        'as_type_id': bono_automatico.id,
                    }
                    self.env['hr.payslip.input'].sudo().create(vals)
                    inp.as_state_payroll = 'asign'
                    inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(res.name), content_subtype='html')  
                else:
                    vals = {
                        'payslip_id':res.id,
                        'input_type_id':discount_automatico_type.id,
                        'amount': inp.bonus_amount,
                        'as_bonus_discount_id': inp.id,
                        'as_type_id': discount_automatico.id,
                    }
                    self.env['hr.payslip.input'].sudo().create(vals)
                    inp.as_state_payroll = 'asign'
                    inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(res.name), content_subtype='html')  
        return res
    
    def get_descuento_abono(self):
        for res in self:
            bono_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','INGRESOS03')])
            bono_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','INGRESOS03')])
            discount_automatico = self.env['as.hr.inputs'].sudo().search([('code', '=','OTRDES3')])
            discount_automatico_type = self.env['hr.payslip.input.type'].sudo().search([('code', '=','OTRDES3')])
            res.input_line_ids.filtered(lambda r: r.input_type_id in (bono_automatico_type,discount_automatico_type)).unlink()
            regsitros =self.env['as.employee.bonus'].sudo().search([('as_date_start', '>=', res.date_from),('as_date_start', '<=', res.date_to),('employee_id', '=', res.employee_id.id),('as_modalidad', '=', 'auto'),('state', '=', 'dapproved_hr_manager')])
            if regsitros:
                for inp in regsitros:
                    existe =self.env['hr.payslip.input'].sudo().search([('payslip_id', '=', res.id),('as_bonus_discount_id', '=', inp.id)])
                    existe.unlink()
                    if inp.as_tipo == 'bonus':
                        vals = {
                            'payslip_id':res.id,
                            'input_type_id':bono_automatico_type.id,
                            'amount': inp.bonus_amount,
                            'as_bonus_discount_id': inp.id,
                            'as_type_id': bono_automatico.id,
                        }
                        self.env['hr.payslip.input'].sudo().create(vals)
                        inp.as_state_payroll = 'asign'
                        inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(res.name), content_subtype='html')  
                    else:
                        vals = {
                            'payslip_id':res.id,
                            'input_type_id':discount_automatico_type.id,
                            'amount': inp.bonus_amount,
                            'as_bonus_discount_id': inp.id,
                            'as_type_id': discount_automatico.id,
                        }
                        self.env['hr.payslip.input'].sudo().create(vals)
                        inp.as_state_payroll = 'asign'
                        inp.message_post(body = 'Asignado '+str(inp.name)+' a '+str(res.name), content_subtype='html')  
            #para caso de anticipos generados de tesoreria
            partner = res.employee_id.user_id.partner_id
            if partner.as_cuenta_employee:
                consulta= ("""
                    select apm.id,aml.date,aml.debit,rp.name from account_move_line aml
                    join account_move am on am.id = aml.move_id
                    join res_partner rp on rp.id=aml.partner_id
                    left join as_payment_multi apm on am.id = apm.account_move_id
                    left join as_tesoreria at on at.id = apm.as_tesoreria_id
                    where aml.account_id = """+str(partner.as_cuenta_employee.id)+""" 
                    and aml.partner_id = """+str(partner.id)+""" 
                    and ((aml.date::TIMESTAMP+ '-4 hr')::date >= '"""+str(res.date_from)+"""' and (aml.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(res.date_to)+"""')
                    and am.state='posted'
                        """)
                self.env.cr.execute(consulta)
                payment = [j for j in self.env.cr.fetchall()]
                for pay in payment:
                    pay_tesoreria = self.env['as.generate.bonus.discount'].search([('as_caja_line_id','in', [pay[0]])])
                    if not pay_tesoreria:
                        vals = {
                            'payslip_id':res.id,
                            'input_type_id':discount_automatico_type.id,
                            'amount': pay[2],
                            'as_type_id': discount_automatico.id,
                        }
                        gp = self.env['hr.payslip.input'].sudo().create(vals)
                        res.message_post(body = 'Asignado '+str(discount_automatico.name)+' a '+str(res.name), content_subtype='html')



    def compute_sheet(self):
        for slip in self:
            slip.get_descuento_abono()
        res = super(HrEmployee, self).compute_sheet()
        return res

    def action_payslip_done(self):
        res = super(HrEmployee, self).action_payslip_done()
        for payslip in self:
            for line in payslip.input_line_ids:
                if line.as_bonus_discount_id:
                    line.as_bonus_discount_id.as_state_payroll = 'done'
                    line.as_bonus_discount_id.state = 'edone'
        return res

    def action_payslip_cancel(self):
        res = super(HrEmployee, self).action_payslip_cancel()
        for payslip in self:
            for line in payslip.input_line_ids:
                if line.as_bonus_discount_id:
                    line.as_bonus_discount_id.as_state_payroll = 'draft'
                    line.as_bonus_discount_id.state = 'dapproved_hr_manager'
        return res